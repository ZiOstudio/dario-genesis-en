"""S0 时基标定：用重生成的伴奏 bed 与母版音轨做互相关，求精确偏移。
原理：full-music.wav 与成片声音层逐采样一致（README 声明），唯一差别是成片里整体 -4.49 dB
并混入了中文旁白。旁白是叠加的干扰项，但包络互相关仍会在真偏移处出现尖峰。
输出：分三段各自求解，若三段一致 => 恒定偏移，无时基漂移。
"""
import numpy as np
import subprocess
import os

SR = 8000           # 分析采样率
HOP = 80            # 100 Hz 包络（10ms 分辨率）
BED = "repo/dario-genesis-main/声音/full-music.wav"
MASTER = "dario-genesis-nosub-1080p.mp4"


def pcm(path, ss=0.0, t=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", path]
    if t:
        cmd += ["-t", str(t)]
    cmd += ["-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    p = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype="<f4").astype(np.float64)


def env(x):
    n = len(x) // HOP
    w = x[: n * HOP].reshape(n, HOP)
    e = np.sqrt((w ** 2).mean(axis=1))
    return e


def best_lag(bed_env, mst_env, lo, hi, mst_off):
    """在 [lo,hi] 秒区间里搜 bed 相对 master 的偏移。"""
    n = len(bed_env)
    best = (-2.0, None, None)
    for lag_ms in range(int(lo * 100), int(hi * 100)):
        m = mst_env[mst_off + lag_ms: mst_off + lag_ms + n]
        if len(m) < n:
            break
        a = bed_env - bed_env.mean()
        b = m - m.mean()
        d = np.linalg.norm(a) * np.linalg.norm(b)
        if d <= 0:
            continue
        c = float(a @ b / d)
        if c > best[0]:
            best = (c, lag_ms / 100.0, d)
    return best


print("载入母版音轨…")
m_all = env(pcm(MASTER))
print(f"母版包络 {len(m_all)} 点 = {len(m_all)/100:.2f}s")

# 三段独立求解：段内取 bed 的一段，在母版里搜 ±10s
segs = [(30.0, 150.0, "第一章"), (300.0, 450.0, "第三/四章"), (540.0, 660.0, "第五章")]
results = []
for s0, s1, name in segs:
    b = env(pcm(BED, ss=s0, t=s1 - s0))
    # 母版里以 s0 为基准，向前后各留 12s 余量搜索
    base = max(0, int((s0 - 12) * 100))
    m = m_all[base: int((s1 + 12) * 100)]
    c, lag, _ = best_lag(b, m, 0.0, (s1 + 12) - max(0, s0 - 12) - (s1 - s0), 0)
    if lag is None:
        print(f"{name}: 无解")
        continue
    off = lag + max(0, s0 - 12) - s0
    results.append(off)
    print(f"{name}: 相关系数 {c:.4f}  偏移 {off:+.2f}s")

if results:
    r = np.array(results)
    print(f"\n三段偏移: {[round(x,2) for x in results]}")
    spread = float(np.ptp(r))
    print(f"均值 {r.mean():+.3f}s  极差 {spread:.3f}s  → " +
          ("恒定偏移，无漂移" if spread < 0.05 else "存在漂移，需分段映射"))
