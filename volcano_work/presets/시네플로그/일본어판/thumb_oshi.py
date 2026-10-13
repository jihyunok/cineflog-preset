# -*- coding: utf-8 -*-
"""일본 벤치 推しシネマ 썸네일 꼴 (2026-10-05 "섬(네일) 일본 벤치 해서 만든거맞아?" → 벤치 칼카피)
1280x720 · 밝고 선명한 인물 한 컷 · 왼쪽 위 플랫폼 이름(벤치는 NETFLIX 빨강) · 왼쪽 아래 짧은 한마디 「まさか…」(흰 글씨, 얇은 검은 테두리 + 그림자) · 다른 글자 없음.
사용: make(src, sec, out, word, cx, cy, zoom, bright, platform="prime video", right=False)"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1280, 720
FW = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/NotoSansJP-Bold.ttf")
FL = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/NotoSansJP-Black.ttf")
def frame(src, sec, cx, cy, zoom):
    tmp = f"_f{sec}.png"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(sec), "-i", src, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGB"); os.remove(tmp); iw, ih = im.size
    ch = ih / zoom; cw = ch * 16 / 9
    if cw > iw: cw = iw; ch = cw * 9 / 16
    x0 = max(0, min(iw - cw, cx * iw - cw / 2)); y0 = max(0, min(ih - ch, cy * ih - ch / 2))
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
def make(src, sec, out, word, cx=0.5, cy=0.4, zoom=1.25, bright=1.2, platform="prime video", right=False):
    im = frame(src, sec, cx, cy, zoom)
    im = ImageEnhance.Brightness(im).enhance(bright); im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.15); im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2))
    # 한마디 — 그림자 먼저
    f = ImageFont.truetype(FW, 150); d = ImageDraw.Draw(im)
    tw = d.textlength(word, font=f); x = W - 45 - tw if right else 45; y = H - 200
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 6, y + 8), word, font=f, fill=(0, 0, 0, 170))
    im = Image.alpha_composite(im.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(8))).convert("RGB")
    d = ImageDraw.Draw(im); d.text((x, y), word, font=f, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    # 플랫폼 이름 — 왼쪽 위
    fl = ImageFont.truetype(FL, 78); d.text((45, 18), platform, font=fl, fill=(0, 168, 225), stroke_width=3, stroke_fill=(0, 0, 0))
    im.save(out, quality=94); return out
