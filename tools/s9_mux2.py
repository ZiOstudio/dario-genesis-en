# -*- coding: utf-8 -*-
"""S9 重压：在片头卡上叠加署名，同时烧英文字幕，沿用已定稿混音轨。
"""
import json
import os
import re
import subprocess

FF = "work/tools/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"
VIDEO = "dario-genesis-nosub-1080p.mp4"
MIX = "work/pcm/mix_final.wav"
SRT = "dario_en.srt"
ASS = "work/credit.ass"
TMP = "work/out_hard.mp4"
FINAL = "dario-genesis-en-1080p.mp4"

STYLE = ("FontName=Segoe UI Semibold,FontSize=14,Bold=0,Outline=1.4,Shadow=1.4,"
         "MarginV=28,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,ShadowColour=&H80000000")

VF = f"ass={ASS},subtitles={SRT}:force_style='{STYLE}'"


def info(path):
    p = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True, errors="replace")
    e = p.stderr
    d = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", e)
    dur = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3))
    return dur, [l.strip() for l in e.splitlines() if "Stream #" in l]


def loud(path):
    p = subprocess.run([FF, "-hide_banner", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, errors="replace")
    t = p.stderr[p.stderr.rfind("Summary:"):]
    return (float(re.search(r"I:\s+(-?\d+\.\d+) LUFS", t).group(1)),
            float(re.search(r"Peak:\s+(-?\d+\.\d+) dBFS", t).group(1)))


for f in (VIDEO, MIX, SRT, ASS):
    if not os.path.exists(f):
        raise SystemExit(f"缺输入：{f}")

print("开始压制…", flush=True)
p = subprocess.run([FF, "-v", "error", "-y", "-i", VIDEO, "-i", MIX,
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-vf", VF,
                    "-c:v", "libx264", "-crf", "18", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
                    "-x264-params", "aq-mode=3",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-movflags", "+faststart",
                    "-metadata", "title=Dario Genesis (English dub)",
                    TMP], capture_output=True, text=True, errors="replace")
if p.returncode != 0:
    print(p.stderr[-2500:])
    raise SystemExit("压制失败")

os.replace(TMP, FINAL)
dur, streams = info(FINAL)
I, TP = loud(FINAL)
print(f"完成 {FINAL}  {os.path.getsize(FINAL)/1048576:.1f} MB  {dur:.2f}s  I={I} LUFS  TP={TP} dBTP")
for s in streams:
    print("  " + s)
json.dump({"file": FINAL, "size_mb": round(os.path.getsize(FINAL) / 1048576, 1),
           "duration": dur, "I": I, "TP": TP, "streams": streams},
          open("work/mux_report_v2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
