# -*- coding: utf-8 -*-
"""S6 混音：人声铺到母版时间轴，与伴奏床合成，片尾从母版音轨直接接续。
配比（实测标定）：
  伴奏床 -6.3 dB → 约 -26 LUFS，真峰 -1.7 dBTP
  人声   +5.0 dB → 约 -16 LUFS，峰顶用 alimiter 收在 -2.0 dBFS
  不做 ducking，稳定不动
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

SR = 48000
FF = "work/tools/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"
PCM = "work/pcm"
BED = "repo/dario-genesis-main/声音/full-music.wav"
MASTER_ST = f"{PCM}/master_st.f32"
VOICE = f"{PCM}/voice.f32"

BED_GAIN = -6.3
VOICE_GAIN = 5.0
GAP = 0.06          # 段尾预留，避免与下一段咬死
TOL = 1e-4
VO_LIM = 0.78        # 人声支路限幅，防止叠加前就削顶


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)


def decode(path, atempo=1.0):
    cmd = [FF, "-v", "error", "-i", path]
    if abs(atempo - 1.0) > 1e-4:
        cmd += ["-filter:a", f"atempo={atempo:.6f}"]
    cmd += ["-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
    return np.frombuffer(run(cmd).stdout, dtype=np.float32)


def probe_dur(path):
    p = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", p.stderr)
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def loud(path):
    p = subprocess.run([FF, "-hide_banner", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, errors="replace")
    tail = p.stderr[p.stderr.rfind("Summary:"):]
    I = float(re.search(r"I:\s+(-?\d+\.\d+) LUFS", tail).group(1))
    TP = float(re.search(r"Peak:\s+(-?\d+\.\d+) dBFS", tail).group(1))
    LRA = float(re.search(r"LRA:\s+(-?\d+\.\d+) LU", tail).group(1))
    return I, TP, LRA


def find_splice():
    """母版 672.5s 后进入数字静默，片尾配乐约 680.3s 淡入。
    取最长静默段的中点作切点，保证不砍断任何乐句。"""
    n = os.path.getsize(MASTER_ST) // 8
    i0 = int(660.0 * SR)
    a = np.fromfile(MASTER_ST, dtype=np.float32, count=(n - i0) * 2, offset=i0 * 8)
    env = np.abs(a.reshape(-1, 2)).max(axis=1)
    quiet = env <= 1e-5
    best = (0, 0)
    run, start = 0, 0
    for i, q in enumerate(quiet):
        if q:
            if run == 0:
                start = i
            run += 1
            if run > best[1]:
                best = (start, run)
        else:
            run = 0
    s0, ln = best
    mid = 660.0 + (s0 + ln / 2) / SR
    return round(mid, 4), 660.0 + s0 / SR, 660.0 + (s0 + ln) / SR, (n / SR)


def build_voice(nar):
    """逐段解码、必要时 atempo 压回窗口、按母版绝对时间轴落位。"""
    total = int(round(TOTAL * SR))
    track = np.zeros(total, dtype=np.float32)
    ids = sorted(nar)
    atempos, clipped = {}, []
    for k, sid in enumerate(ids):
        src = f"work/tts/en/{sid}.mp3"
        if not os.path.exists(src) or os.path.getsize(src) < 2000:
            raise SystemExit(f"缺音频：{src}")
        s = nar[sid]
        start = s["master_start"]
        nxt = nar[ids[k + 1]]["master_start"] if k + 1 < len(ids) else TOTAL
        window = min(s["duration"], nxt - start - GAP)
        window = max(window, 0.4)
        v = decode(src)
        d = len(v) / SR
        if d > window:
            f = d / window
            atempos[sid] = round(f, 4)
            v = decode(src, f)
            d = len(v) / SR
        i0 = int(round(start * SR))
        seg = v[: max(0, total - i0)]
        track[i0:i0 + len(seg)] += seg
        if d > window + 0.02:
            clipped.append((sid, round(d - window, 3)))
    track.tofile(VOICE)
    return track, atempos, clipped


def main():
    global TOTAL
    nar = {s["id"]: s for s in json.load(open("work/narration.json", encoding="utf-8"))["segments"]}
    splice, q0, q1, TOTAL = find_splice()
    print(f"总长 {TOTAL:.3f}s  片尾切入 {splice:.3f}s（静默区 {q0:.3f}–{q1:.3f}s）", flush=True)

    track, atempos, clipped = build_voice(nar)
    pk = float(np.abs(track).max())
    print(f"人声轨峰值 {pk:.3f} ({20*np.log10(pk):+.1f} dBFS)，"
          f"atempo 压缩段 {atempos or '无'}，残留超窗 {clipped or '无'}", flush=True)
    del track

    delay_ms = int(round(splice * 1000))
    graph = (
        f"[0:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo,"
        f"atrim=0:{splice},asetpts=N/SR/TB,volume={BED_GAIN}dB[bed];"
        f"[1:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=mono,"
        f"volume={VOICE_GAIN}dB,alimiter=level=0:latency=1:limit={VO_LIM}:attack=4:release=80,"
        f"pan=stereo|c0=c0|c1=c0[vo];"
        f"[2:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo,"
        f"atrim={splice}:{TOTAL},asetpts=N/SR/TB,adelay={delay_ms}|{delay_ms}[tail];"
        f"[bed][vo][tail]amix=inputs=3:normalize=0:duration=longest,"
        f"apad=whole_dur={TOTAL},atrim=0:{TOTAL}[m]"
    )
    run([FF, "-v", "error", "-y", "-i", BED,
         "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", VOICE,
         "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", MASTER_ST,
         "-filter_complex", graph, "-map", "[m]", "-c:a", "pcm_f32le", f"{PCM}/mix_pre.wav"])
    I, TP, LRA = loud(f"{PCM}/mix_pre.wav")
    print(f"混后  I={I} LUFS  TP={TP} dBTP  LRA={LRA} LU", flush=True)

    # 定增益，再用关闭自动增益的真峰限幅器收顶；限幅过狠就放宽，不够就收紧
    g = round(TARGET_I - I, 2)
    lim = 0.74
    for attempt in range(1, 5):
        print(f"  第 {attempt} 次：增益 {g:+.2f} dB，限幅 {20*np.log10(lim):.2f} dBFS", flush=True)
        run([FF, "-v", "error", "-y", "-i", f"{PCM}/mix_pre.wav",
             "-af", f"volume={g}dB,alimiter=level=0:latency=1:limit={lim}:attack=3:release=70",
             "-c:a", "pcm_f32le", f"{PCM}/mix_final.wav"])
        I2, TP2, LRA2 = loud(f"{PCM}/mix_final.wav")
        print(f"    得到 I={I2} LUFS  TP={TP2} dBTP", flush=True)
        if TP2 <= -1.35 and abs(I2 - TARGET_I) <= 0.4:
            break
        if TP2 > -1.25:
            lim = round(lim * 10 ** (-0.6 / 20), 4)
        if abs(I2 - TARGET_I) > 0.4:
            g = round(g + (TARGET_I - I2), 2)
    print(f"成品  I={I2} LUFS  TP={TP2} dBTP  LRA={LRA2} LU", flush=True)
    chk = subprocess.run([FF, "-v", "error", "-i", f"{PCM}/mix_final.wav",
                          "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True)
    arr = np.frombuffer(chk.stdout, dtype=np.float32)
    over = int((np.abs(arr) > 1.0).sum())
    print(f"过载样本 {over} 个，峰值 {float(np.abs(arr).max()):.4f}", flush=True)
    json.dump({"bed_gain_db": BED_GAIN, "voice_gain_db": VOICE_GAIN, "splice": splice,
               "total": TOTAL, "pre": {"I": I, "TP": TP, "LRA": LRA},
               "final": {"I": I2, "TP": TP2, "LRA": LRA2}, "gain": g,
               "atempo": atempos},
              open("work/mix_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


TARGET_I = -15.5
TOTAL = None
main()
