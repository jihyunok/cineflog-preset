# -*- coding: utf-8 -*-
"""오이시드라마 썸네일 글자 그대로 + 괴기스러운 효과 (2026-10-06 사용자: "바람 섬네일은 이렇게하지말고 / 오이시스타일로 글자체랑 똑같이해줘 / 글자에 괴기스러운 효과도 들어가게")
오이시 글자 실측(lPGrvTtMZ4Y 확대): 붓으로 그은 굵은 빨강, 획 끝 뾰족, 획 안에 검은 긁힘 결, 바깥은 두꺼운 검은 테두리 + 번진 검은 그림자.
- 붓 글꼴: 레코체(굵은 붓글씨, 설치된 것 중 오이시 굵기에 가장 가까움) — 오이시 원 글꼴은 확인 못 함
- 효과: 획 안 검은·검붉은 긁힘 결 + 아래로 흐르는 핏물 몇 줄 + 두꺼운 검은 테두리 + 번진 검은 그림자
- 위: 초록 괄호 한마디(오이시처럼 둥근 굵은 글씨 = 잘난체)
사용: make(src, sec, out, bottom, top=None, cx=.5, cy=.42, zoom=1, bright=1.08, seed=1)"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import thumb_ref as R
FD = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/")
BRUSH = FD + "Recipekorea 레코체 FONT.ttf"; ROUND = FD + "Jalnan2TTF.ttf"
DOHYEON = os.path.expanduser(r"~/volcano_work/fonts/DoHyeon-Regular.ttf")   # 10-06 "크게 눕혀서 도현체로"
W, H = R.W, R.H
RED, GREEN = (235, 8, 8), (40, 235, 30)
SLANT = 0.12

def fit(text, font, maxw, sz):
    d = ImageDraw.Draw(Image.new("L", (8, 8)))
    while sz > 30:
        f = ImageFont.truetype(font, sz)
        if d.textlength(text, font=f) <= maxw: return f, sz
        sz -= 2
    return ImageFont.truetype(font, sz), sz

def shear(L, yc, sl=None):
    sl = SLANT if sl is None else sl
    return L.transform((W, H), Image.AFFINE, (1, sl, -sl * yc, 0, 1, 0), Image.BICUBIC)

def horror(base, text, y_bottom, rnd, font=BRUSH, sl=None, maxsz=200, effect=True):
    f, sz = fit(text, font, W * 0.9, maxsz)
    d = ImageDraw.Draw(Image.new("L", (8, 8))); bb = d.textbbox((0, 0), text, font=f)
    x = (W - (bb[2] - bb[0])) / 2 - bb[0]; y = y_bottom - bb[3]
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).text((x, y), text, font=f, fill=255)
    box = m.getbbox()
    # 핏물: 글자 아래 가장자리에서 아래로 흐르는 줄
    drip = Image.new("L", (W, H), 0); dd = ImageDraw.Draw(drip); px = m.load()
    for _ in range(int(len(text) * 1.1) if effect else 0):
        for _try in range(60):
            cx = rnd.randint(box[0], box[2] - 1); col = [yy for yy in range(box[1], box[3]) if px[cx, yy] > 128]
            if col: break
        else: continue
        y0 = col[-1]; ln = rnd.randint(int(sz * 0.12), int(sz * 0.45)); w = rnd.randint(6, 12)
        dd.rounded_rectangle((cx - w / 2, y0 - 4, cx + w / 2, y0 + ln), radius=w // 2, fill=255)
        dd.ellipse((cx - w * 0.9, y0 + ln - w * 0.9, cx + w * 0.9, y0 + ln + w * 0.9), fill=255)
    shape = ImageChops.lighter(m, drip)
    # 번진 검은 그림자 + 두꺼운 테두리
    glow = shape.filter(ImageFilter.MaxFilter(45)).filter(ImageFilter.GaussianBlur(16))
    edge = shape.filter(ImageFilter.MaxFilter(29))
    yc = (box[1] + box[3]) / 2
    for L, a in ((glow, 235), (edge, 255)):
        L = shear(L.point(lambda v: min(255, int(v * a / 255 * 1.4))), yc, sl)
        base.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), L)
    # 빨강 + 긁힘 결
    fill = Image.new("RGB", (W, H), RED); fd = ImageDraw.Draw(fill)
    for _ in range(int((box[2] - box[0]) * (0.13 if font == DOHYEON else 0.3)) if effect else 0):
        sx = rnd.uniform(box[0], box[2]); sy = rnd.uniform(box[1], box[3]); ln = rnd.uniform(sz * 0.08, sz * 0.4)
        ang = rnd.uniform(-0.35, 0.35); c = rnd.choice([(40, 0, 0), (110, 0, 0), (160, 0, 0)])
        fd.line((sx, sy, sx + ln * ang, sy + ln), fill=c, width=rnd.choice([1, 2, 2, 3]))
    for _ in range(int((box[2] - box[0]) * (0.05 if font == DOHYEON else 0.12)) if effect else 0):          # 가로 붓 결
        sx = rnd.uniform(box[0], box[2]); sy = rnd.uniform(box[1], box[3]); ln = rnd.uniform(sz * 0.1, sz * 0.35)
        fd.line((sx, sy, sx + ln, sy + rnd.uniform(-6, 6)), fill=rnd.choice([(60, 0, 0), (0, 0, 0)]), width=rnd.choice([1, 2]))
    fill = fill.filter(ImageFilter.GaussianBlur(0.6))
    base.paste(shear(fill, yc, sl), (0, 0), shear(shape, yc, sl))

def green(base, text, font=ROUND, sl=None, gsz=76):
    f, s = fit(text, font, W * 0.86, gsz)
    d = ImageDraw.Draw(Image.new("L", (8, 8))); bb = d.textbbox((0, 0), text, font=f)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(L).text(((W - (bb[2] - bb[0])) / 2 - bb[0], 22 - bb[1]), text, font=f, fill=GREEN, stroke_width=max(6, int(s * 0.13)), stroke_fill=(0, 0, 0))
    b = L.getbbox(); L = shear(L, (b[1] + b[3]) / 2, sl); base.paste(L, (0, 0), L)

def make(src, sec, out, bottom, top=None, cx=0.5, cy=0.42, zoom=1.0, bright=1.08, seed=1, font=BRUSH, sl=None, maxsz=200, effect=True, gsz=76):
    rnd = random.Random(seed)
    im = R.grade(R.frame(src, sec, cx, cy, zoom, out), bright)
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for y in range(int(H * 0.6), H): d.line((0, y, W, y), fill=int(150 * ((y - H * 0.6) / (H * 0.4)) ** 1.2))
    for y in range(int(H * 0.2)): d.line((0, y, W, y), fill=int(110 * (1 - y / (H * 0.2))))
    base = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, m)
    horror(base, bottom, H - (56 if font == DOHYEON else 34), rnd, font, sl, maxsz, effect)
    if top: green(base, top, DOHYEON if font == DOHYEON else ROUND, sl, gsz)
    base.save(out, quality=93); return out
