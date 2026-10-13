# -*- coding: utf-8 -*-
"""시네플로그 썸네일 — 사용자가 준 참고 캡처 꼴 (2026-10-01 "이런스타일로", 「누구부터 죽여줄까」).
밝고 선명한 사진, 인물 하나 꽉 · 아래 한 줄 아주 큰 굵은 고딕(살짝 눕힘 SLANT) · 앞말 흰색 + 뒷말 빨강 · 두꺼운 검은 테두리 · 짧고 센 한마디.
사용(모듈): make(src, sec, out, white, red, cx=.5, cy=.42, zoom=1, bright=1.08)"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

FONT = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/Pretendard-Black.otf")
W, H = 1280, 720
WHITE, RED = (255, 255, 255), (235, 16, 22)
SLANT = 0.2                                      # 기울기(가로 밀림 비율)

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
    im = ImageEnhance.Color(im).enhance(1.3)
    return im.filter(ImageFilter.UnsharpMask(radius=2.5, percent=130, threshold=2))

def make(src, sec, out, white, red, cx=0.5, cy=0.42, zoom=1.0, bright=1.08):
    im = grade(frame(src, sec, cx, cy, zoom, out), bright)
    # 아래 글자 자리만 살짝 어둡게
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    y0 = int(H * 0.62)
    for y in range(y0, H):
        d.line((0, y, W, y), fill=int(150 * ((y - y0) / (H - y0)) ** 1.3))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, m)
    base = im; im = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # 글자판 따로 → 살짝 눕혀서 얹는다
    d = ImageDraw.Draw(im)
    gap = 0.28                                       # 두 말 사이 띄움(글자 크기 비율)
    sz = 200
    while True:
        f = ImageFont.truetype(FONT, sz)
        tw = d.textlength(white, font=f) + d.textlength(red, font=f) + sz * gap
        if tw <= W * 0.93 or sz < 60: break
        sz -= 2
    st = max(8, int(sz * 0.085))
    asc = f.getbbox(white + red)
    x = (W - tw) / 2; y = H - (asc[3]) - 34
    for t, c in ((white, WHITE), (red, RED)):
        d.text((x, y), t, font=f, fill=c, stroke_width=st, stroke_fill=(0, 0, 0))
        x += d.textlength(t, font=f) + sz * gap
    # 살짝 눕히기 ("글자체 저렇게 말고 살작 눕히고") — 글자 줄 가운데를 기준으로 기울임
    sh, yc = SLANT, y + sz * 0.6
    im = im.transform((W, H), Image.AFFINE, (1, sh, -sh * yc, 0, 1, 0), Image.BICUBIC)
    base.paste(im, (0, 0), im)
    base.save(out, quality=93); return out
