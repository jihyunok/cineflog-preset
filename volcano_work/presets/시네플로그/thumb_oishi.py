# -*- coding: utf-8 -*-
"""오이시드라마 썸네일 꼴 (2026-10-06 사용자: "로드하우스섬네일바바 너무약하지않니 / 오이시섬네일보면 / 글자크기도 작고")
- 아래: 아주 큰 도현체 빨강 + 아주 두꺼운 검은 테두리, 한 줄, 화면 폭 92%
- 위: 초록 괄호 한마디 (도현체), 검은 테두리
- 선택: 흰 따옴표 대사 하나(얼굴 옆)
사용: make(src, sec, out, bottom, top=None, quote=None, qx=.7, qy=.4, cx=.5, cy=.42, zoom=1, bright=1.08)"""
import os
from PIL import Image, ImageDraw, ImageFont
import thumb_ref as R
FD = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/")
# 10-06 사용자: "글자체를 이걸로하지말고 도현체로하고" → 위·아래 모두 배민 도현체(구글 폰트 Do Hyeon, OFL)
BRUSH = ROUND = os.path.expanduser(r"~/volcano_work/fonts/DoHyeon-Regular.ttf")
W, H = R.W, R.H
SLANT = 0.2
RED, GREEN, WHITE, YEL = (240, 12, 12), (30, 235, 40), (255, 255, 255), (255, 240, 0)

def fit(d, text, font, maxw, sz):
    while sz > 30:
        f = ImageFont.truetype(font, sz)
        if d.textlength(text, font=f) <= maxw: return f, sz
        sz -= 2
    return ImageFont.truetype(font, sz), sz

def put(base, xy, text, font, fill, sw):
    """한 줄을 따로 그려 그 줄 가운데를 기준으로 눕혀 얹는다(줄마다 자리 그대로)."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(L).text(xy, text, font=font, fill=fill, stroke_width=sw, stroke_fill=(0, 0, 0))
    bb = L.getbbox(); yc = (bb[1] + bb[3]) / 2
    L = L.transform((W, H), Image.AFFINE, (1, SLANT, -SLANT * yc, 0, 1, 0), Image.BICUBIC)
    base.paste(L, (0, 0), L)

def make(src, sec, out, bottom, top=None, quote=None, qx=0.72, qy=0.42, cx=0.5, cy=0.42, zoom=1.0, bright=1.08, bottom_color=RED, quote_color=None):
    im = R.grade(R.frame(src, sec, cx, cy, zoom, out), bright)
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for y in range(int(H * 0.6), H): d.line((0, y, W, y), fill=int(170 * ((y - H * 0.6) / (H * 0.4)) ** 1.2))
    for y in range(int(H * 0.2)): d.line((0, y, W, y), fill=int(120 * (1 - y / (H * 0.2))))
    base = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, m)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)   # 글자판 따로 → 눕혀서 얹는다
    f, sz = fit(d, bottom, BRUSH, W * 0.88, 190)
    bb = d.textbbox((0, 0), bottom, font=f); tw = bb[2] - bb[0]
    put(base, ((W - tw) / 2 - bb[0], H - bb[3] - 26), bottom, f, bottom_color, max(10, int(sz * 0.11)))
    if top:
        f2, s2 = fit(d, top, ROUND, W * 0.86, 74)
        bb = d.textbbox((0, 0), top, font=f2)
        put(base, ((W - (bb[2] - bb[0])) / 2 - bb[0], 22 - bb[1]), top, f2, GREEN, max(6, int(s2 * 0.12)))
    if quote:
        f3, s3 = fit(d, quote, ROUND, W * 0.45, 70)
        bb = d.textbbox((0, 0), quote, font=f3)
        put(base, (qx * W - (bb[2] - bb[0]) / 2, qy * H), quote, f3, quote_color or WHITE, max(6, int(s3 * 0.12)))
    # 10-06 사용자: "글자눕히고" → 글자판 전체를 SLANT 만큼 기울인다(가운데 기준)
    base.save(out, quality=93); return out


def make_top(src, sec, out, top_red, quote_green, cx=0.5, cy=0.42, zoom=1.0, bright=1.08):
    """며느라기 꼴(오이시 dK2TiCXgPKI): 위 빨강 「결말까지 몰아보기」 + 아래 큰 초록 대사, 도현체·눕힘."""
    im = R.grade(R.frame(src, sec, cx, cy, zoom, out), bright)
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for y in range(int(H * 0.7), H): d.line((0, y, W, y), fill=int(140 * (max(0, y - H * 0.7) / (H * 0.3)) ** 1.2))
    for y in range(int(H * 0.3)): d.line((0, y, W, y), fill=int(110 * (1 - y / (H * 0.3))))
    base = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, m)
    d = ImageDraw.Draw(Image.new("RGBA", (W, H)))
    f, sz = fit(d, top_red, BRUSH, W * 0.94, 170)
    bb = d.textbbox((0, 0), top_red, font=f)
    put(base, ((W - (bb[2] - bb[0])) / 2 - bb[0], 18 - bb[1]), top_red, f, RED, max(10, int(sz * 0.11)))
    f2, s2 = fit(d, quote_green, BRUSH, W * 0.94, 150)
    bb = d.textbbox((0, 0), quote_green, font=f2)
    put(base, ((W - (bb[2] - bb[0])) / 2 - bb[0], H - bb[3] - 24), quote_green, f2, GREEN, max(10, int(s2 * 0.11)))
    base.save(out, quality=93); return out
