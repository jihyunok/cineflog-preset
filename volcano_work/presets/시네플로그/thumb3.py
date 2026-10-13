# -*- coding: utf-8 -*-
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
F = None
for p in [os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/Pretendard-Black.otf"), r"C:/Windows/Fonts/Pretendard-Black.otf"]:
    if os.path.exists(p): F = p
def make(sec, parts, out, cx=0.5):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(sec), "-i", "src.mp4", "-frames:v", "1", f"th/f{sec}.png"], check=True)
    im = Image.open(f"th/f{sec}.png").convert("RGB")      # 1920x804 → 16:9 로 잘라 1280x720
    w = int(800 * 16 / 9); x0 = int(max(0, min(1920 - w, cx * 1920 - w / 2)))
    im = im.crop((x0, 0, x0 + w, 800)).resize((1280, 720), Image.LANCZOS)
    if sec == 2030:
        from PIL import ImageEnhance; im = ImageEnhance.Brightness(im).enhance(1.9)
    d = ImageDraw.Draw(im); size = 104
    while True:
        f = ImageFont.truetype(F, size); tw = sum(d.textlength(t, font=f) for t, _ in parts)
        if tw < 1200: break
        size -= 4
    x = (1280 - tw) / 2; y = 720 - size - 70
    for t, col in parts:
        d.text((x, y), t, font=f, fill=col, stroke_width=10, stroke_fill="black"); x += d.textlength(t, font=f)
    im.save(out, quality=92)
W, Y = "white", "#FFE400"
make(4085, [("피범벅으로 받은 ", W), ("입양", Y), (" 전화", W)], "th/A.jpg", 0.5)
make(5113, [("경찰 여섯 명이 ", W), ("쫓아온", Y), (" 이유", W)], "th/B.jpg", 0.5)
make(2030, [("시골 할머니 집의 ", W), ("악몽", Y)], "th/C.jpg", 0.45)
