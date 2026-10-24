"""S4-全量：合成全部段落，用「时长 ∝ 1/(1+rate)」模型求解语速，使贴合原段时长。
用法：python s4b_tts_all.py [--force]
产物：work/tts/en/<sid>.mp3 + work/tts/fit_report.json（合并写回）
"""
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys

import edge_tts

sys.path.insert(0, "work")
from en_clauses import EN

VOICE = "en-US-AndrewMultilingualNeural"
FFMPEG = r"D:\ffmpeg"
OUT = "work/tts/en"
REPORT = "work/tts/fit_report.json"
os.makedirs(OUT, exist_ok=True)

RATE_MIN, RATE_MAX = -25, 32
TOL = 0.013
MAXCALL = 6
JOBS = 4

# 直连会被微软侧按源 IP 限流（表现为 TLS 握手失败），代理稳定且更快
PROXY = "http://127.0.0.1:7897"
STATE = {"proxy": PROXY}


def dur(path):
    p = subprocess.run([FFMPEG, "-hide_banner", "-i", path],
                       capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", p.stderr)
    if not m:
        return 0.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def seg_text(sid):
    t = " ".join(p for p in EN[sid]).replace("|", " ")
    return " ".join(t.split())


async def synth(text, path, rate, tries=5):
    """用 stream() 自己落盘：实测 Communicate.save() 偶发写 0 字节并挂死。"""
    last = None
    for i in range(tries):
        try:
            async def collect():
                c = edge_tts.Communicate(text, VOICE, rate=rate,
                                         proxy=STATE["proxy"], receive_timeout=45,
                                         connect_timeout=15)
                buf = []
                async for ch in c.stream():
                    if ch["type"] == "audio":
                        buf.append(ch["data"])
                return b"".join(buf)

            data = await asyncio.wait_for(collect(), timeout=100)
            if len(data) > 2000:
                with open(path, "wb") as f:
                    f.write(data)
                d = dur(path)
                if d > 0.2:
                    return True, d
                last = f"时长异常 {d}"
            else:
                last = f"音频过短 {len(data)}B"
        except Exception as e:                      # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
        await asyncio.sleep(0.8 * (i + 1))
    print(f"    !! {os.path.basename(path)} rate={rate} 失败：{last}", flush=True)
    return False, 0.0


def next_rate(meas, target):
    """meas: {rate:int -> dur:float}。模型 dur ≈ A/(1+rate/100)，用 A 的中位数反解。"""
    if not meas:
        return 0
    A = sorted(d * (1 + r / 100.0) for r, d in meas.items())[len(meas) // 2]
    s = A / target
    r = (s - 1) * 100
    r = max(RATE_MIN, min(RATE_MAX, r))
    r = int(round(r))
    guard = 0
    while r in meas and guard < 40:
        r += 1 if r >= 0 else -1
        guard += 1
    return max(RATE_MIN, min(RATE_MAX, r))


async def fit(sid, target):
    text = seg_text(sid)
    final = os.path.join(OUT, f"{sid}.mp3")
    tmp = os.path.join(OUT, f"_{sid}.{os.getpid()}.tmp.mp3")
    meas, best = {}, None
    for _ in range(MAXCALL):
        r = next_rate(meas, target)
        ok, d = await synth(text, tmp, f"{r:+d}%")
        if not ok:
            break
        meas[r] = d
        err = abs(d - target)
        if best is None or err < best[0]:
            shutil.copyfile(tmp, final)
            best = (err, r, d)
        if err <= max(0.05, target * TOL):
            break
    if os.path.exists(tmp):
        os.remove(tmp)
    if best is None:
        return None, 0.0
    return meas, best[2]


async def main(force=False, only=None):
    nar = {s["id"]: s for s in json.load(open("work/narration.json", encoding="utf-8"))["segments"]}
    ids = sorted(nar)
    if only:
        ids = [i for i in ids if i in only]
    rep = json.load(open(REPORT, encoding="utf-8")) if os.path.exists(REPORT) else {}

    todo = []
    for sid in ids:
        p = os.path.join(OUT, f"{sid}.mp3")
        good = (os.path.exists(p) and os.path.getsize(p) > 2000 and sid in rep
                and abs(rep[sid]["final"] - nar[sid]["duration"])
                <= max(0.05, nar[sid]["duration"] * TOL))
        if force or not good:
            todo.append(sid)
    print(f"总 {len(ids)} 段，待合成 {len(todo)}：{' '.join(todo) or '无'}\n", flush=True)

    fail, worst = [], []
    sem = asyncio.Semaphore(JOBS)
    done = [0]
    lock = asyncio.Lock()

    async def worker(sid):
        target = nar[sid]["duration"]
        async with sem:
            meas, final = await fit(sid, target)
        async with lock:
            if not meas:
                fail.append(sid)
                return
            dev = (final - target) / target * 100
            rep[sid] = {"target": round(target, 3), "final": round(final, 3),
                        "dev": f"{dev:+.1f}%",
                        "measured": {str(k): round(v, 3) for k, v in sorted(meas.items())},
                        "words": len(seg_text(sid).split()), "text": seg_text(sid),
                        "overflow": round(max(0.0, final - target), 3)}
            if abs(dev) > 2.5:
                worst.append((sid, round(dev, 1)))
            done[0] += 1
            print(f"[{done[0]:>2}/{len(todo)}] {sid} 目标 {target:6.2f} 实得 {final:6.2f} "
                  f"偏差 {dev:+5.1f}% 档位 {sorted(meas)}", flush=True)
            json.dump(rep, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    await asyncio.gather(*(worker(s) for s in todo))

    print("\n=== 汇总 ===", flush=True)
    over = [(s, rep[s]["overflow"]) for s in ids if s in rep and rep[s].get("overflow", 0) > 0.12]
    miss = [s for s in ids if s not in rep]
    print(f"已合成 {len(rep)}/{len(ids)}  失败 {fail or '无'}  缺 {miss or '无'}")
    print(f"偏差 >2.5% 的段：{worst or '无'}")
    if over:
        print("超窗段（铺排时用 atempo 压回）：" + "  ".join(f"{s}+{o:.2f}s" for s, o in over))
    else:
        print("无超窗段。")
    json.dump(rep, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


args = [a for a in sys.argv[1:] if not a.startswith("--")]
for a in sys.argv[1:]:
    if a.startswith("--jobs="):
        JOBS = int(a.split("=")[1])
asyncio.run(main("--force" in sys.argv, set(args) or None))
