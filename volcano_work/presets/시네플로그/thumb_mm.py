# -*- coding: utf-8 -*-
"""시네플로그 썸네일 — 선생님 채널 「무비 MASTER」(UCul4FTKARC-EaBq0e8UH7RA) 꼴 (2026-10-01 벤치 실측).
밝고 쨍한 사진(어둡게 누르지 않음) · 아주 굵은 고딕을 기울여 · 노랑 글씨+검은 테두리+그림자 · 핵심어는 크게/빨강/흰색
· 문구는 인물 말투("3초 준다! 이거 치워..") · 한 줄 또는 (작은 줄 + 큰 줄).
사용(모듈): make(src, sec, out, lines, cx=.5, zoom=1, bright=1.08, top=False)
  lines = [[(글자, 색, 크기배율), ...], ...]  색: Y 노랑 / W 흰 / R 빨강"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

FONT = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/GmarketSansBold.otf")
if not os.path.exists(FONT): FONT = "C:/Windows/Fonts/GmarketSansBold.otf"
COL = {"Y": (255, 228, 0), "W": (255, 255, 255), "R": (240, 20, 20)}
W, H = 1280, 720

def frame(src, sec, cx, cy, zoom, out):
    tmp = os.path.splitext(out)[0] + "_raw.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(sec), "-i", src, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGB"); os.remove(tmp)
    iw, ih = im.size; ch = ih / zoom; cw = ch * 16 / 9
    if cw > iw: cw = iw; ch = cw * 9 / 16
    x0 = max(0, min(iw - cw, cx * iw - cw / 2)); y0 = max(0, min(ih - ch, cy * ih - ch / 2))
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)

def grade(im, bright):
    im = ImageEnhance.Brightness(im).enhance(bright)
    im = ImageEnhance.Contrast(im).enhance(1.15)
    im = ImageEnhance.Color(im).enhance(1.35)
    im = im.filter(ImageFilter.UnsharpMask(radius=2.5, percent=130, threshold=2))
    return im

def text_layer(lines, base):
    """줄마다 크기를 맞춰 RGBA 글자판을 만든다(가로 90% 안)."""
    L = Image.new("RGBA", (W * 2, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    def width(line, b): return sum(d.textlength(t, font=ImageFont.truetype(FONT, int(b * s))) for t, _, s in line)
    b = base
    while max(width(l, b) for l in lines) > W * 0.9 and b > 40: b -= 2
    y = 0; boxes = []
    for line in lines:
        hmax = max(int(b * s) for _, _, s in line)
        x = (W - width(line, b)) / 2 + W / 2
        for t, c, s in line:
            f = ImageFont.truetype(FONT, int(b * s)); yy = y + (hmax - int(b * s)) * 0.85
            d.text((x, yy), t, font=f, fill=COL[c], stroke_width=max(6, int(b * s * 0.09)), stroke_fill=(0, 0, 0))
            x += d.textlength(t, font=f)
        y += int(hmax * 1.12)
    L = L.crop((0, 0, W * 2, y + 20))
    # 기울이기(이탤릭)
    sh = 0.18
    L = L.transform(L.size, Image.AFFINE, (1, sh, -sh * L.size[1] * 0.5, 0, 1, 0), Image.BICUBIC)
    return L.crop((W // 2, 0, W // 2 + W, L.size[1]))

def make(src, sec, out, lines, cx=0.5, zoom=1.0, bright=1.08, top=False, base=96):
    im = grade(frame(src, sec, cx, 0.42, zoom, out), bright)
    T = text_layer(lines, base)
    y = 34 if top else H - T.size[1] - 26
    shadow = Image.new("RGBA", T.size, (0, 0, 0, 0)); shadow.putalpha(T.getchannel("A").point(lambda v: int(v * 0.75)))
    im.paste(shadow.filter(ImageFilter.GaussianBlur(7)), (8, y + 9), shadow.filter(ImageFilter.GaussianBlur(7)))
    im.paste(T, (0, y), T)
    im.save(out, quality=93); return out
