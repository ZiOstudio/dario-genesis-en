"""S3 生成 SRT（v4）。
改动 vs v3：
  1) 断行以句子为最小单位——句子未结束不跨行，避免 "And distillation…"/"Rules" 这类碎行
  2) 取消自动首字母大写——译稿本身已按句子编码大小写，自动大写反而破坏续行
  3) 修掉窗口重叠导致的负时长
时间策略不变：段内按字数比例分配（行速均匀，天然单调）。
"""
import sys
import json

sys.path.insert(0, "work")
from en_clauses import EN

MAXLEN = 42
MIN_DUR = 0.85
GAP_EXTEND = 1.0
END_SENT = (".", "!", "?", ".”", "!”", "?”", "…")

clauses = json.load(open("work/clauses.json", encoding="utf-8"))
sids = list(clauses.keys())


def ts(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"


def pieces(zh, en_list):
    assert len(zh) == len(en_list), f"子句数不匹配 {len(zh)} vs {len(en_list)}"
    out = []
    for c, en in zip(zh, en_list):
        en = en.strip()
        if not en:
            continue
        out.extend([p.strip() for p in en.split("|") if p.strip()])
    return out


def wrap(text):
    """单条文本超长时按词边界切分（不跨句），并对末尾孤字做回填再平衡。"""
    if len(text) <= MAXLEN:
        return [text]
    lines, cur = [], ""
    for w in text.split():
        cand = (cur + " " + w).strip()
        if len(cand) <= MAXLEN:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    # 再平衡：末行过短时，从上一行搬词下来
    for _ in range(3):
        if len(lines) < 2:
            break
        if len(lines[-1]) >= 14:
            break
        prev = lines[-2].split()
        if len(prev) < 3:
            break
        moved = prev[-1]
        cand = moved + " " + lines[-1]
        if len(cand) > MAXLEN:
            break
        lines[-2] = " ".join(prev[:-1])
        lines[-1] = cand
    return lines


def group(texts):
    """按句子边界分组：上一行若已句末，且长度≥15，则不合并下一条。"""
    units = []
    for t in texts:
        units.extend(wrap(t))
    lines = []
    for u in units:
        if lines:
            prev = lines[-1]
            cand = prev + " " + u
            done = prev.rstrip().endswith(END_SENT) and len(prev) >= 15
            if len(cand) <= MAXLEN and not done:
                lines[-1] = cand
                continue
        lines.append(u)
    return lines


def allocate(texts, w0, w1):
    span = max(w1 - w0, 0.2)
    total = sum(map(len, texts))
    floor_w = total * MIN_DUR / span
    w = [max(len(t), floor_w) for t in texts]
    sw = sum(w)
    bounds, acc = [w0], w0
    for x in w[:-1]:
        acc += span * x / sw
        bounds.append(acc)
    bounds.append(w1)
    return [(texts[i], bounds[i], bounds[i + 1]) for i in range(len(texts))]


entries, over, notes = [], [], []
for k, sid in enumerate(sids):
    zh = clauses[sid]
    texts = group(pieces(zh, EN[sid]))
    if not texts:
        continue
    w0 = zh[0]["start"]
    w1 = zh[-1]["end"]
    nxt = clauses[sids[k + 1]][0]["start"] if k + 1 < len(sids) else 703.5
    limit = nxt - 0.08
    w1 = min(w1, limit)
    if limit - w1 > 0.2:
        w1 = min(w1 + GAP_EXTEND, limit)
    if w1 <= w0 + 0.2:
        notes.append(f"{sid} 窗口异常 {w0:.2f}->{w1:.2f}")
        w1 = w0 + 0.2
    for text, s, e in allocate(texts, w0, w1):
        t = text.strip()
        if not t:
            continue
        cps = len(t) / max(e - s, 0.01)
        if cps > 20:
            over.append((round(cps, 1), sid, len(t), round(e - s, 2), t))
        entries.append([s, e, t, cps])

entries.sort(key=lambda x: x[0])
for i in range(1, len(entries)):
    pe = entries[i - 1][1]
    if entries[i][0] < pe + 0.01:
        entries[i][0] = pe + 0.01
    if entries[i][1] <= entries[i][0] + 0.05:
        entries[i][1] = entries[i][0] + 0.3

with open("work/dario_en.srt", "w", encoding="utf-8", newline="\n") as f:
    for n, (s, e, t, _) in enumerate(entries, 1):
        f.write(f"{n}\n{ts(s)} --> {ts(e)}\n{t}\n\n")

lens = [len(t) for _, _, t, _ in entries]
durs = [e - s for s, e, t, _ in entries]
cs = [c for *_, c in entries]
print(f"条目 {len(entries)}   词数 {sum(len(t.split()) for _,_,t,_ in entries)}")
print(f"行长度 max {max(lens)} / 平均 {sum(lens)/len(lens):.1f}")
print(f"时长 min {min(durs):.2f}s / 平均 {sum(durs)/len(durs):.2f}s / max {max(durs):.2f}s")
print(f"CPS 平均 {sum(cs)/len(cs):.1f} / max {max(cs):.1f}   超20的 {len(over)} 条")
print(f"覆盖 {entries[0][0]:.2f} → {entries[-1][1]:.2f}s")
if notes:
    print("窗口异常:", notes)
