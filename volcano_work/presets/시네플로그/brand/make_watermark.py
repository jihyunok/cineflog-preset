# -*- coding: utf-8 -*-
"""「대작」 워터마크 — 10-20 사용자 "그리고 대작 워터마크 무드킹처럼 만들어"(무드킹 fK2xpgBdMJM 오른쪽 위 로고를 보고).
무드킹 꼴: 네모진 굵은 글씨 · 위 주황 → 아래 노랑 그러데이션 · 어두운 테두리 · 마지막 글자 위에 금빛 왕관 · 살짝 비침.
→ brand/대작_워터마크.png(투명 배경, 1080p 기준 글자 높이 약 72px). build_v9(롱폼 오른쪽 위)·shorts_tpl(쇼츠 영상 자리 오른쪽 위)이 이 그림을 얹는다.
사용: python make_watermark.py [글꼴파일] [출력.png] [글자]   (글꼴 기본 = 지마켓 산스 굵게 — 10-20 글꼴 다섯 개 견줘 무드킹 네모진 글씨에 가장 가까움)
★10-20 이 PC(시네플로그)로 가져옴: 글자를 셋째 인자로 바꿀 수 있게(기본 「대작」). 쓰려면 ep.json "brand_png": "<출력 이름>.png" — 안 적으면 롱폼·쇼츠 모두 옛 CINEFLOG 글자."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts")
FONT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(FD, "GmarketSansTTFBold.ttf")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "대작_워터마크.png")
TEXT, SZ, OPA = (sys.argv[3] if len(sys.argv) > 3 else "「대작」"), 92, 0.88
CROWN = False   # ★10-20 텔레그램 "대작에 왕관은 빼고 처음세 넣었던 기호 넣어. 색상은 지금처럼해" → 「」 넣고 왕관 뺌(색은 그대로)
TOP, BOT, EDGE = (243, 150, 18), (255, 214, 40), (40, 24, 0)


def grad(w, h, a, b):
    g = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h - 1); d.line([(0, y), (w, y)], fill=tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,))
    return g


def crown(w):
    """금빛 왕관(가운데 뾰족 셋 + 구슬) — 폭 w"""
    h = round(w * 0.62); m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
    base = h * 0.78; r = w * 0.07
    pts = [(w * 0.08, base), (w * 0.02, h * 0.30), (w * 0.30, h * 0.52), (w * 0.50, h * 0.12), (w * 0.70, h * 0.52), (w * 0.98, h * 0.30), (w * 0.92, base)]
    d.polygon(pts, fill=255); d.rectangle([w * 0.08, base - 1, w * 0.92, h * 0.97], fill=255)
    for x, y in ((w * 0.02, h * 0.30), (w * 0.50, h * 0.12), (w * 0.98, h * 0.30)): d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    g = grad(w, h, (255, 236, 120), (214, 150, 20)); g.putalpha(m)
    edge = Image.new("RGBA", (w, h), EDGE + (255,)); edge.putalpha(m.filter(ImageFilter.MaxFilter(3)))
    out = Image.alpha_composite(edge, g)
    band = ImageDraw.Draw(out); band.rectangle([w * 0.10, base + 2, w * 0.90, base + max(3, h * 0.07)], fill=(170, 105, 10, 255))
    return out


fo = ImageFont.truetype(FONT, SZ)
x0, y0, x1, y1 = fo.getbbox(TEXT); tw, th = x1 - x0, y1 - y0
cw = round(SZ * 0.62); cr = crown(cw); pad = 10
W = tw + pad * 2 + 8; H = th + (cr.height - round(cr.height * 0.18) if CROWN else 0) + pad * 2
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ty = H - pad - th
m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).text((pad - x0, ty - y0), TEXT, font=fo, fill=255)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(m.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3)).point(lambda v: v * 0.6))
edge = Image.new("RGBA", (W, H), EDGE + (255,)); edge.putalpha(m.filter(ImageFilter.MaxFilter(7)))
body = grad(W, H, TOP, BOT); body.putalpha(m)
img = Image.alpha_composite(img, sh); img = Image.alpha_composite(img, edge); img = Image.alpha_composite(img, body)
# 왕관: 마지막 글자 오른쪽 위에 걸쳐(무드킹 「킹」 위처럼)
lx = fo.getbbox(TEXT[:-1])[2] if len(TEXT) > 1 else 0; last_w = x1 - lx
cx = pad - x0 + lx + last_w * 0.55 - cw / 2; cy = ty - cr.height + round(cr.height * 0.18)
if CROWN: img.alpha_composite(cr, (max(0, min(W - cw, round(cx))), max(0, round(cy))))
a = img.getchannel("A").point(lambda v: round(v * OPA)); img.putalpha(a)
img.save(OUT); print(OUT, img.size)
