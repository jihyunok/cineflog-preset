# -*- coding: utf-8 -*-
"""thumb_ref 꼴 + 화면 위 후킹 한마디.
2026-10-03 사용자: "화면위에 형광연녹색으로 후킹되는말 한마디" → "연두색글자가 너무 길어 너 분석한거맞아?" →
[캡처: 드림텔러 「싸움의 신」 / 영반 「조폭 VS 조선족」] "이런스타일" ★확정 = 위 한마디도 **흰 앞말 + 빨간 뒷말**, 크기 100(아래 큰 글씨의 약 55%), 검은 테두리 10, 기울이지 않음, 짧게(2~8자).
사용: make(src, sec, out, white, red, top_white, top_red, cx, cy, zoom, bright)  /  over(이미 만든 jpg, out, top_white, top_red)"""
from PIL import Image, ImageDraw, ImageFont
import thumb_ref as R

def over(path, out, tw_, tr_, sz=100):
    assert len((tw_ + tr_).replace(" ", "")) <= 9, "위 한마디는 9자 이하"
    im = Image.open(path).convert("RGB"); W, H = im.size
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m); y1 = int(H * 0.26)
    for y in range(y1): d.line((0, y, W, y), fill=int(110 * (1 - y / y1) ** 1.4))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, m)
    f = ImageFont.truetype(R.FONT, sz); d = ImageDraw.Draw(im); g = sz * 0.24
    tw = d.textlength(tw_, font=f) + g + d.textlength(tr_, font=f); x = (W - tw) / 2
    for t, c in ((tw_, R.WHITE), (tr_, R.RED)):
        d.text((x, 22), t, font=f, fill=c, stroke_width=int(sz * 0.1), stroke_fill=(0, 0, 0)); x += d.textlength(t, font=f) + g
    im.save(out, quality=93); return out

def make(src, sec, out, white, red, top_white, top_red, cx=0.5, cy=0.42, zoom=1.0, bright=1.08):
    R.make(src, sec, out, white, red, cx, cy, zoom, bright)
    return over(out, out, top_white, top_red)
