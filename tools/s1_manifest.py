"""S1 生成时基表与旁白清单：把 数据/ch*.js 的章内时间统一换算到母版时间轴。
母版时间 = 章节偏移 + 段内 start + TIME_OFFSET
"""
import json
import os
import re
import glob

OFFSET = 3.05067          # S0 实测：146432 / 48000，六窗口极差 0ms
CHAPTERS = [              # 偏移取自各章作曲脚本 docstring，已互相验证
    ("ch1.js", "一｜起初", 0.0),
    ("ch2.js", "二｜请停止理解宇宙", 190.5333),
    ("ch3.js", "三｜服务持续优化", 353.1333),
    ("ch4.js", "四｜其他用户的下场", 421.86667),
    ("ch5.js", "五｜最后一次复核", 518.1333),
]
BASE = "repo/dario-genesis-main/数据"
OUT = "work"

segments = []
for fn, title, coff in CHAPTERS:
    raw = open(os.path.join(BASE, fn), encoding="utf-8").read()
    d = json.loads(re.match(r"\s*window\.\w+\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S).group(1))
    for p in d["parts"]:
        text = p["text"]
        ct = p["charTimes"]
        n_cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
        g_start = coff + p["start"] + OFFSET
        g_end = coff + p["end"] + OFFSET
        dur = g_end - g_start
        segments.append({
            "chapter": title,
            "id": p["id"],
            "text": text,
            "cjk_chars": n_cjk,
            "master_start": round(g_start, 3),
            "master_end": round(g_end, 3),
            "duration": round(dur, 3),
            "word_budget": int(round(dur * 2.5)),      # 150 wpm ≈ 2.5 词/秒
            "charTimes_local": ct[:1] + ct[-1:],        # 仅保留首尾，全量在源文件里
        })

segments.sort(key=lambda s: s["master_start"])
total_cjk = sum(s["cjk_chars"] for s in segments)
total_dur = sum(s["duration"] for s in segments)
total_words = sum(s["word_budget"] for s in segments)

tb = {
    "master_file": "dario-genesis-nosub-1080p.mp4",
    "master_duration": 703.928,
    "fps": 30,
    "audio_offset_sec": OFFSET,
    "audio_offset_samples_48k": round(OFFSET * 48000),
    "method": "重生成伴奏 full-music.wav 与母版音轨波形互相关，6 个时间窗独立求解",
    "evidence": {
        "spread_ms": 0.0,
        "peak_sharpness": "偏移 3.0429(+8ms) 时相关系数由 0.505 崩至 0.036",
        "video_cut_at": 3.04206,
        "note": "视频切点 3.042s 与音频 3.0507s 相差 9ms，不足 1/3 帧"
    },
    "formula": "master_time = chapter_offset + part.start + 3.05067",
    "chapter_offsets": {t: o for _, t, o in CHAPTERS},
    "bed_coverage": {"start": 0.0, "end": 681.6666,
                     "tail_gap": "681.67–703.93 为片尾字幕卡配乐，需从母版截取"}
}

with open(os.path.join(OUT, "timebase.json"), "w", encoding="utf-8") as f:
    json.dump(tb, f, ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "narration.json"), "w", encoding="utf-8") as f:
    json.dump({"segments": segments, "total_cjk": total_cjk,
               "total_duration": round(total_dur, 2),
               "total_word_budget": total_words}, f, ensure_ascii=False, indent=1)

print(f"段数 {len(segments)}   中文字 {total_cjk}   旁白总时长 {total_dur:.1f}s")
print(f"英文词预算合计 {total_words} 词（150 wpm 口径）")
print(f"母版时间轴 {tb['master_duration']}s，末段结束于 {segments[-1]['master_end']}s")
print("\n首 5 段:")
for s in segments[:5]:
    print(f"  {s['id']}  {s['master_start']:>7.2f}–{s['master_end']:>7.2f}  "
          f"{s['duration']:>5.2f}s  {s['cjk_chars']:>3}字  {s['word_budget']:>3}词  "
          f"{s['text'][:24]}")
print("\n末 2 段:")
for s in segments[-2:]:
    print(f"  {s['id']}  {s['master_start']:>7.2f}–{s['master_end']:>7.2f}  "
          f"{s['text'][:28]}")
