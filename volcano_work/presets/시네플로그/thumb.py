# -*- coding: utf-8 -*-
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
F = None
for p in [os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/Pretendard-Black.otf"), r"C:/Windows/Fonts/Pretendard-Black.otf"]:
    if os.path.exists(p): F = p
def make(sec, parts, out, cx=0.5):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(sec), "-i", "src.mp4", "-frames:v", "1", f"th/f{sec}.png"], check=True)
    im = Image.open(f"th/f{sec}.png").convert("RGB")      # 1920x804 → 16:9 로 잘라 1280x720
    w = int(804 * 16 / 9); x0 = int(max(0, min(1920 - w, cx * 1920 - w / 2)))
    im = im.crop((x0, 0, x0 + w, 804)).resize((1280, 720), Image.LANCZOS)
    if sec == 2130:
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
make(890, [("아기 안고 ", W), ("킬러", Y), (" 잡는 아빠?", W)], "th/A.jpg", 0.28)
make(925, [("중고차 딜러 아빠의 ", W), ("정체", Y)], "th/B.jpg", 0.85)
make(2130, [("가족 몰래 ", W), ("18년", Y), (" 숨긴 비밀", W)], "th/C.jpg", 0.55)
