"""独立校验 SRT：格式、序号、单调性、行长度、CPS。"""
import re

P = "work/dario_en.srt"
raw = open(P, encoding="utf-8").read()
blocks = [b for b in raw.strip().split("\n\n") if b.strip()]

TS = re.compile(r"^(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})$")


def sec(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


prev_end = -1.0
bad = []
rows = []
for i, b in enumerate(blocks, 1):
    L = b.split("\n")
    if len(L) != 3:
        bad.append((i, f"行数 {len(L)}"))
        continue
    if L[0].strip() != str(i):
        bad.append((i, f"序号 {L[0]!r}"))
    m = TS.match(L[1].strip())
    if not m:
        bad.append((i, f"时间码 {L[1]!r}"))
        continue
    g = m.groups()
    s, e = sec(*g[:4]), sec(*g[4:])
    if e <= s:
        bad.append((i, "时长<=0"))
    if s < prev_end - 0.001:
        bad.append((i, f"重叠 {s:.2f}<{prev_end:.2f}"))
    if len(L[2]) > 42:
        bad.append((i, f"超长 {len(L[2])}"))
    if not L[2].strip():
        bad.append((i, "空文本"))
    prev_end = e
    rows.append((s, e, L[2]))

cps = [len(t) / (e - s) for s, e, t in rows]
print(f"块数 {len(blocks)}   问题 {len(bad)} 项")
for b in bad[:8]:
    print("  ", b)
print(f"文件 {len(raw.encode('utf-8'))} 字节 / UTF-8 / LF")
print(f"时长 min {min(e-s for s,e,_ in rows):.2f}s  max {max(e-s for s,e,_ in rows):.2f}s")
print(f"CPS avg {sum(cps)/len(cps):.1f}  max {max(cps):.1f}")
print(f"覆盖 {rows[0][0]:.2f}s → {rows[-1][1]:.2f}s")

print("\n—— 前 10 块 ——")
print("\n\n".join(blocks[:10]))
print("\n—— 末 4 块 ——")
print("\n\n".join(blocks[-4:]))
