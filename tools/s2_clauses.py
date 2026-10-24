"""把每段中文按标点切成子句，并用 charTimes（逐字符边界）读出每个子句的精确起止。
产出 work/clauses.json：{段id: [{zh, start, end, dur}, ...]}
用途：英文按同样子句数翻译，即可一对一继承时间，无需 TTS 词级对齐。
"""
import json
import os
import re

SRC = "work/narration.json"
BASE = "repo/dario-genesis-main/数据"
CHAPTERS = [("ch1.js", 0.0), ("ch2.js", 190.5333), ("ch3.js", 353.1333),
            ("ch4.js", 421.86667), ("ch5.js", 518.1333)]
OFFSET = 3.05067
PUNCT = "，。：；！？、…"          # 中文切分标点（不含引号，引号不切）

# 先把每段原文与 charTimes 读回来
raw_parts = {}
for fn, coff in CHAPTERS:
    raw = open(os.path.join(BASE, fn), encoding="utf-8").read()
    d = json.loads(re.match(r"\s*window\.\w+\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S).group(1))
    for p in d["parts"]:
        raw_parts[p["id"]] = {"text": p["text"], "ct": p["charTimes"],
                              "coff": coff, "start": p["start"], "end": p["end"]}

narration = json.load(open(SRC, encoding="utf-8"))
out = {}
for seg in narration["segments"]:
    sid = seg["id"]
    rp = raw_parts[sid]
    text, ct = rp["text"], rp["ct"]
    # charTimes 与 text 一一对应（含换行），逐字符定位
    assert len(ct) == len(text) + 1, (sid, len(ct), len(text))
    base = rp["coff"] + rp["start"] + OFFSET - rp["start"]  # 章偏移+全局偏移
    clauses = []
    cur_start_idx = None
    for i, ch in enumerate(text):
        if ch in "\n":
            continue
        if cur_start_idx is None:
            cur_start_idx = i
        if ch in PUNCT or ch in "”\"" and i + 1 < len(text) and text[i + 1] in PUNCT:
            j = i + 1
            if ch in PUNCT:
                while j < len(text) and text[j] in PUNCT:
                    j += 1
            zh = text[cur_start_idx:j].strip()
            if zh:
                s = base + ct[cur_start_idx]
                e = base + ct[j]
                clauses.append({"zh": zh, "start": round(s, 3), "end": round(e, 3),
                                "dur": round(e - s, 3)})
            cur_start_idx = None
    if cur_start_idx is not None:
        zh = text[cur_start_idx:].strip()
        if zh:
            s = base + ct[cur_start_idx]
            e = base + ct[-1]
            clauses.append({"zh": zh, "start": round(s, 3), "end": round(e, 3),
                            "dur": round(e - s, 3)})
    out[sid] = clauses

tot = sum(len(v) for v in out.values())
print(f"段数 {len(out)}   子句总数 {tot}")
lens = [c["dur"] for v in out.values() for c in v]
print(f"子句时长: 最短 {min(lens):.2f}s  中位 {sorted(lens)[len(lens)//2]:.2f}s  最长 {max(lens):.2f}s")
print(f"短子句(<0.9s) {sum(1 for x in lens if x<0.9)} 个")
json.dump(out, open("work/clauses.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n样例 S01:")
for c in out["S01"]:
    print(f"  {c['start']:>7.2f}-{c['end']:>7.2f} ({c['dur']:>4.2f}s) {c['zh']}")
