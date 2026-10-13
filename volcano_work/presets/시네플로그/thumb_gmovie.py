# -*- coding: utf-8 -*-
"""시네플로그 썸네일 — 지무비(G Movie) 꼴 (2026-10-01 "썸네일너무구려" 뒤 벤치 실측).
벤치: 인물 하나 크게 · 진한 색보정+비네트 · 아래 한 줄 굵은 명조(흰 + 핵심 빨강) · 테두리 대신 그림자 · 가끔 빨간 !?
사용: python thumb_gmovie.py <원본영상> <초> <나갈.jpg> <글자> [빨강부분] [cx 0~1] [zoom] [밝기] [!?]
   글자 중 빨강부분 문자열만 빨갛게. cx = 얼굴 가로 위치, zoom = 1.0 이상이면 더 당김."""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

FONT = "C:/Windows/Fonts/NotoSerifKR-VF.ttf"
RED, WHITE = (235, 20, 20), (255, 255, 255)
W, H = 1280, 720

def font(sz):
    f = ImageFont.truetype(FONT, sz); f.set_variation_by_name("Black"); return f

def frame(src, sec, cx, cy, zoom):
    tmp = os.path.splitext(sys.argv[3])[0] + "_raw.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(sec), "-i", src, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGB"); os.remove(tmp)
    iw, ih = im.size
    ch = ih / zoom; cw = ch * 16 / 9
    if cw > iw: cw = iw; ch = cw * 9 / 16
    x0 = max(0, min(iw - cw, cx * iw - cw / 2)); y0 = max(0, min(ih - ch, cy * ih - ch / 2))
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)

def grade(im, bright):
    im = ImageEnhance.Brightness(im).enhance(bright)
    im = ImageEnhance.Contrast(im).enhance(1.18)
    im = ImageEnhance.Color(im).enhance(1.25)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=90, threshold=2))
    # 비네트 + 아래쪽 어둡게(글자 자리)
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for i in range(60):
        a = int(150 * (1 - i / 60) ** 2)
        d.rectangle((i * 6, i * 4, W - i * 6, H - i * 4), outline=a, width=7)
    for y in range(H // 2, H):
        v = int(170 * ((y - H / 2) / (H / 2)) ** 1.6)
        d.line((0, y, W, y), fill=max(v, m.getpixel((W // 2, y))))
    return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, m.filter(ImageFilter.GaussianBlur(25)))

def text(im, txt, red, bang):
    d = ImageDraw.Draw(im)
    sz = 120
    while True:
        f = font(sz); tw = d.textlength(txt, font=f)
        if tw <= W * 0.88 or sz < 50: break
        sz -= 2
    x, y = (W - tw) / 2, H - sz - 62
    i = txt.find(red) if red else -1
    parts = [(txt, WHITE)] if i < 0 else [(txt[:i], WHITE), (red, RED), (txt[i + len(red):], WHITE)]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh); xx = x
    for t, _ in parts:
        sd.text((xx + 5, y + 6), t, font=f, fill=(0, 0, 0, 230)); xx += d.textlength(t, font=f)
    im.paste(sh.filter(ImageFilter.GaussianBlur(6)), (0, 0), sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im); xx = x
    for t, c in parts:
        d.text((xx, y), t, font=f, fill=c, stroke_width=2, stroke_fill=(20, 0, 0)); xx += d.textlength(t, font=f)
    if bang:
        fb = font(170); d.text((W - 230, 40), "!?", font=fb, fill=RED, stroke_width=4, stroke_fill=(30, 0, 0))
    return im

if __name__ == "__main__":
    a = sys.argv
    src, sec, out, txt = a[1], float(a[2]), a[3], a[4]
    red = a[5] if len(a) > 5 else ""
    cx = float(a[6]) if len(a) > 6 else 0.5
    zoom = float(a[7]) if len(a) > 7 else 1.0
    bright = float(a[8]) if len(a) > 8 else 1.0
    bang = len(a) > 9 and a[9] == "!?"
    cy = 0.42
    im = text(grade(frame(src, sec, cx, cy, zoom), bright), txt, red, bang)
    im.save(out, quality=93); print(out)
