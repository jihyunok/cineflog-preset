# -*- coding: utf-8 -*-
"""17 그레이하운드 썸네일 — 벤치(U무비) 꼴: 밝고 선명한 배 장면 + 왼쪽 아래 큰 흰 글씨·두꺼운 검은 테두리(한 줄). 장면·문구는 우리 것.
사용: python thumb17.py 원본초 "문구" 출력.jpg [x0=가로 시작] [h=자를 높이(박힌 자막 위까지)]"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
t, text, out = float(sys.argv[1]), sys.argv[2], sys.argv[3]
x0 = int(sys.argv[4]) if len(sys.argv) > 4 else -1; hh = int(sys.argv[5]) if len(sys.argv) > 5 else 690
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", "C:/Users/uere/Downloads/그레이하운드.mp4", "-frames:v", "1", "_th.png"], check=True)
im = Image.open("_th.png").convert("RGB"); ww = round(hh * 16 / 9)
if x0 < 0: x0 = (1920 - ww) // 2
im = im.crop((x0, 0, x0 + ww, hh)).resize((1280, 720), Image.LANCZOS)
im = ImageEnhance.Brightness(im).enhance(1.5); im = ImageEnhance.Contrast(im).enhance(1.2); im = ImageEnhance.Color(im).enhance(1.3)
im = im.filter(ImageFilter.UnsharpMask(radius=2.5, percent=170, threshold=2))
d = ImageDraw.Draw(im); F = ImageFont.truetype(r"C:/Windows/Fonts/BlackHanSans-Regular.ttf", 132)
d.text((34, 715), text, font=F, fill="white", anchor="ls", stroke_width=11, stroke_fill="black")
im.save(out, quality=95); os.remove("_th.png"); print(out)
