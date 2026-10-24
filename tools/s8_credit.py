# -*- coding: utf-8 -*-
"""生成片头署名卡的 ASS 覆盖层。
沿用原卡片节奏：块间距 84px、块内行距 58px、米白 RGB(235,226,220)、居中 x=960。
时间：0.20s 淡入（200ms），保持到 3.00s（原卡片 3.03s 切走）。
"""
import json
import os
import subprocess
import sys

FF = "work/tools/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"
OUT_ASS = "work/credit.ass"

# 可调参数（改这里就能微调）
FONT_CJK = "Noto Serif SC"
FONT_LAT = "Noto Serif SC"
SZ_CJK = 48
SZ_LAT = 44
Y_CJK = 860
Y_LAT = 916
CREAM = "&H00B7B4A5"      # 中文署名：冷灰蓝 RGB(165,180,183)
DIM   = "&H00908C78"      # 英文署名：更深一档 RGB(120,140,144)
T_START = "0:00:00.20"
T_END = "0:00:03.03"    # ASS 时间码只收两位百分秒；原卡末帧 3.000s，次帧 3.033s 切走

ZH = "英文翻译及后期：@zihao_ZiO"
EN = "English translation & post-production: @zihao_ZiO"

HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Card,%s,%d,%s,%s,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: CardLat,%s,%d,%s,%s,&H00000000,&H00000000,0,0,0,0,100,100,0.8,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (FONT_CJK, SZ_CJK, CREAM, CREAM, FONT_LAT, SZ_LAT, DIM, DIM)


def main():
    body = (f"Dialogue: 0,{T_START},{T_END},Card,,0,0,0,,"
            f"{{\\pos(960,{Y_CJK})\\fad(200,0)}}{ZH}\n"
            f"Dialogue: 0,{T_START},{T_END},CardLat,,0,0,0,,"
            f"{{\\pos(960,{Y_LAT})\\fad(200,0)}}{EN}\n")
    open(OUT_ASS, "w", encoding="utf-8").write(HEAD + body)
    print(f"写入 {OUT_ASS}")

    subprocess.run([FF, "-v", "error", "-y", "-i", "dario-genesis-nosub-1080p.mp4",
                    "-ss", "2.0", "-frames:v", "1",
                    "-vf", f"ass={OUT_ASS}", "work/probe/card_test.png"], check=True)
    print("渲染 work/probe/card_test.png")


main()
