# -*- coding: utf-8 -*-
"""벤치 썸네일 꼴(사용자 10-12 "섬네일이런스타일이야 선명하게"): 로봇 얼굴 크게 + 왼쪽 아래 두 줄
노랑 「평점 9.4」 · 빨강 「진짜 존X 재밌음」, 잘난체, 두꺼운 검은 테두리. 선명·밝게. 사용: python thumb_v5.py 초 출력.jpg"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
t, out = float(sys.argv[1]), sys.argv[2]
x0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", "../ep16v4_핀치/src.mp4", "-frames:v", "1", "_th.png"], check=True)
im = Image.open("_th.png").convert("RGB").crop((x0, 0, x0 + 1429, 804)).resize((1920, 1080), Image.LANCZOS)
im = ImageEnhance.Brightness(im).enhance(1.45); im = ImageEnhance.Contrast(im).enhance(1.15); im = ImageEnhance.Color(im).enhance(1.25)
im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=160, threshold=2))
F = os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/Jalnan2TTF.ttf")
d = ImageDraw.Draw(im)
def line(text, size, y, fill):
    f = ImageFont.truetype(F, size)
    d.text((95, y), text, font=f, fill=fill, stroke_width=int(size * 0.11), stroke_fill="black")
line("평점 9.4", 190, 560, (255, 245, 0))
line("진짜 존X 재밌음", 190, 790, (255, 20, 20))
im.save(out, quality=95); os.remove("_th.png"); print(out)
