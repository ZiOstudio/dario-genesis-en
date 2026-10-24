"""S0c 偏移定解：先用合成信号锁定 correlate 的索引约定，再在真实数据上求解并直接验证。
不再依赖我的符号推导——先证明约定，再用约定。
"""
import numpy as np
from scipy.signal import correlate
import os

SR = 48000
D = "work/pcm"


def load(name, nsamp=None):
    p = os.path.join(D, name)
    n = os.path.getsize(p) // 4
    return np.memmap(p, dtype="<f4", mode="r", shape=(n,))


bed = load("bed.f32")
mst = load("master.f32")
print(f"bed {len(bed)/SR:.3f}s   master {len(mst)/SR:.3f}s")

# ---------- 1. 用合成信号确认索引约定 ----------
rng = np.random.default_rng(0)
y = rng.standard_normal(4800)                 # 0.1s 探针
X = np.zeros(48000)
KNOWN = 12000                                 # 把探针放在 X 的第 12000 个采样
X[KNOWN:KNOWN + 4800] = y
c = correlate(X, y, mode="valid")
i = int(np.argmax(c))
print(f"[约定测试] 探针实际位置 {KNOWN}，argmax 索引 {i} → "
      f"offset = k - 0 = {i}  ({'一致' if i == KNOWN else '不一致，需 +len(y)-1'})")
LAG_OFFSET = KNOWN - i
print(f"[约定测试] 需要补偿的常数 = {LAG_OFFSET}")


def scan(t0, win=60.0, pad=6.0):
    """返回 (最佳偏移秒, 相关系数)。offset 含义：master 时间 = bed 时间 + offset"""
    a = int(t0 * SR)
    n = int(win * SR)
    p = int(pad * SR)
    y = np.asarray(bed[a:a + n], dtype=np.float64)
    x = np.asarray(mst[max(0, a - p): a + n + p], dtype=np.float64)
    lead = max(0, a - p)
    y = y - y.mean()
    x = x - x.mean()
    c = correlate(x, y, mode="valid")
    cs = np.concatenate([[0.0], np.cumsum(x ** 2)])
    e = np.sqrt(np.maximum(cs[n:] - cs[:-n], 1e-12)) * np.linalg.norm(y)
    r = c / e
    k = int(np.argmax(r))
    off = (k + LAG_OFFSET) / SR + (lead - a) / SR
    return off, float(r[k])


print(f"\n{'时间窗':<10}{'偏移(s)':>11}{'相关':>9}")
offs = []
for t0 in [40, 150, 260, 380, 500, 600]:
    off, r = scan(t0)
    offs.append(off)
    print(f"{t0:<10}{off:>11.5f}{r:>9.3f}")

offs = np.array(offs)
print(f"\n均值 {offs.mean():+.5f}s   极差 {np.ptp(offs)*1000:.3f}ms")

# ---------- 2. 直接验证：按求得的偏移逐点对齐，看相关系数 ----------
print("\n[直接验证] bed[t0:t0+10] 与 master[t0+off : t0+off+10] 的相关系数")
best = float(offs.mean())
for t0 in [40, 150, 380, 590]:
    a = int(t0 * SR)
    n = 10 * SR
    y = np.asarray(bed[a:a + n], dtype=np.float64)
    y -= y.mean()
    for cand, tag in [(best, "求得值"), (best + 5.0, "+5s"), (best - 5.0, "-5s"),
                      (3.0429, "标题卡推算"), (-1.9573, "旧结果")]:
        s = int(round((t0 + cand) * SR))
        if s < 0 or s + n > len(mst):
            print(f"  t0={t0:<4} {tag:<10} 越界"); continue
        x = np.asarray(mst[s:s + n], dtype=np.float64)
        x -= x.mean()
        r = float(y @ x / (np.linalg.norm(y) * np.linalg.norm(x)))
        print(f"  t0={t0:<4} {tag:<10} off={cand:+.4f}  r={r:+.4f}")
    print()
