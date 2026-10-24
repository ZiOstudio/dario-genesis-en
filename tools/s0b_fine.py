"""S0b 波形级精相关：把偏移从 ±50ms 压到 ±1 采样（0.02ms）。
依据：成片音轨 ≈ a·bed + b·旁白（同一声学层，线性混合后做响度标准化）。
旁白是随机干扰项，波形互相关在真偏移处会给出尖锐 δ 峰，邻点迅速衰减。
"""
import numpy as np
from scipy.signal import correlate, correlation_lags
import subprocess

SR = 48000
BED = "repo/dario-genesis-main/声音/full-music.wav"
MASTER = "dario-genesis-nosub-1080p.mp4"


def pcm(path, ss, t):
    c = ["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-i", path,
         "-t", f"{t:.3f}", "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    p = subprocess.run(c, capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype="<f4").astype(np.float64)


def fine_offset(t0, win=20.0, pad=5.0):
    x = pcm(MASTER, t0, win + 2 * pad)          # 母版：以 t0-pad 起
    y = pcm(BED, t0, win)                        # bed：正好 t0..t0+win
    n = len(y)
    if len(x) < n + int(pad * SR):
        return None
    x = x - x.mean()
    y = y - y.mean()
    c = correlate(x, y, mode="valid", method="fft")
    lags = correlation_lags(len(x), len(y), mode="valid")
    # 归一化：滑动能量
    cs = np.concatenate([[0.0], np.cumsum(x ** 2)])
    e = np.sqrt(np.maximum(cs[n:] - cs[:-n], 1e-12)) * np.linalg.norm(y)
    r = c / e
    i = int(np.argmax(r))
    peak = float(r[i])
    lag_s = (lags[i] - pad * SR) / SR            # 负值表示 bed 滞后于母版
    # 峰旁边衰减：判断是否尖锐
    nb = r[max(0, i - 240): i + 240]             # ±5ms 邻域
    drop = peak - float(np.median(nb))
    return -lag_s, peak, drop                     # 返回「母版时间 = bed时间 + off」


print(f"{'时间窗':<14}{'偏移(s)':>10}{'相关':>9}{'峰对比':>9}")
res = []
for t0 in [40.0, 200.0, 360.0, 470.0, 590.0]:
    r = fine_offset(t0)
    if r is None:
        print(f"{t0:<14.0f}  窗口不足")
        continue
    off, pk, drop = r
    res.append(off)
    print(f"{t0:<14.0f}{off:>10.5f}{pk:>9.3f}{drop:>9.3f}")

a = np.array(res)
print(f"\n偏移样本 {[round(v,4) for v in res]}")
print(f"均值 {a.mean():+.5f}s   极差 {np.ptp(a)*1000:.2f}ms")
print(f"换算帧数 {a.mean()*30:.2f} 帧（30fps）")
