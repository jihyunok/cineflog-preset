# -*- coding: utf-8 -*-
"""시네플로그 썸네일 — 카랑 꼴(그레이하운드 164만 OQwyicCcA1s): 선명한 장면 + 빨간 굵은 글자 한 줄을 비스듬히 크게 「퐉」.
빨강 채움 + 획 안 밝은 긁힘 결 + 두꺼운 검은 테두리 + 아래로 번진 그림자, 왼쪽 아래→오른쪽 위로 기울임.
(10-14 사용자 "섬네일이이게뭐냐" / "섬네일은 눈에 띄게 빨간글자로 퐉!!" / "급박한장면을 묘사하는문장을 넣어야지" / "안나와도 상관없어")
사용: python thumb_karang.py 원본.mp4|그림.png 초 "문장" 출력.jpg x0 y0 h [글자자리 cx cy] [최대폭비] [기울기도] [글꼴 bhs|reco|dh]
  x0 y0 h = 원본에서 16:9 로 자를 왼쪽·위·높이(h=0 이면 그림 통째) · 글자자리 cx cy 는 0~1 비율 · 기울기 도(+면 오른쪽 위로)
17 그레이하운드: 1 = AI 그림(agy_image.py, ep 폴더 thumb_ai_battle.png) 0 0 0 0.5 0.16 0.9 4 「사방이 잠수함이다!」
                 2 = 원본 4210초 기운 구축함 120 0 802 0.5 0.8 0.92 5 「어뢰 충돌 1초 전!」"""
import os, sys, random, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
W, H = 1280, 720
FONTS = {"bhs": r"C:/Windows/Fonts/BlackHanSans-Regular.ttf",
         "reco": os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/Recipekorea 레코체 FONT.ttf"),
         "dh": os.path.expanduser(r"~/volcano_work/fonts/DoHyeon-Regular.ttf")}
RED = (238, 18, 18)

def picture(src, sec, x0, y0, hh):
    if src.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        im = Image.open(src).convert("RGB")
    else:
        tmp = "_k.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(sec), "-i", src, "-frames:v", "1", tmp], check=True)
        im = Image.open(tmp).convert("RGB"); os.remove(tmp)
    if hh > 0:
        ww = round(hh * 16 / 9); im = im.crop((x0, y0, x0 + ww, y0 + hh))
    im = im.resize((W, H), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=0.4)
    im = ImageEnhance.Color(im).enhance(1.35); im = ImageEnhance.Brightness(im).enhance(1.08)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))

def red_text(base, text, cx, cy, maxw, deg, font, seed=3):
    rnd = random.Random(seed); sz = 260
    while sz > 40:
        f = ImageFont.truetype(font, sz); bb = ImageDraw.Draw(Image.new("L", (8, 8))).textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= maxw * W: break
        sz -= 4
    tw, th = bb[2] - bb[0], bb[3] - bb[1]; pad = 60; CW, CH = tw + pad * 2, th + pad * 2
    m = Image.new("L", (CW, CH), 0); ImageDraw.Draw(m).text((pad - bb[0], pad - bb[1]), text, font=f, fill=255)
    edge = m.filter(ImageFilter.MaxFilter(2 * max(9, sz // 14) + 1))
    shadow = edge.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10))
    fill = Image.new("RGB", (CW, CH), RED); fd = ImageDraw.Draw(fill)
    for _ in range(int(tw * 0.10)):                      # 획 안 긁힘 결(카랑 글자처럼 밝은 줄·어두운 줄)
        sx, sy = rnd.uniform(pad, pad + tw), rnd.uniform(pad, pad + th); ln = rnd.uniform(sz * 0.08, sz * 0.3)
        c = rnd.choice([(255, 120, 110), (150, 0, 0), (120, 0, 0)])
        fd.line((sx, sy, sx + ln * rnd.uniform(-0.25, 0.25), sy + ln), fill=c, width=rnd.choice([1, 2, 2]))
    lay = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    lay.paste((0, 0, 0, 200), (14, 16), shadow.point(lambda v: v * 200 // 255).crop((0, 0, CW - 14, CH - 16)))
    lay.paste((0, 0, 0, 255), (0, 0), edge)
    lay.paste(fill.filter(ImageFilter.GaussianBlur(0.5)), (0, 0), m)
    lay = lay.rotate(deg, resample=Image.BICUBIC, expand=True)
    base.paste(lay, (int(cx * W - lay.width / 2), int(cy * H - lay.height / 2)), lay)

if __name__ == "__main__":
    a = sys.argv[1:]
    src, sec, text, out = a[0], float(a[1]), a[2], a[3]
    x0, y0, hh = int(a[4]), int(a[5]), int(a[6])
    cx = float(a[7]) if len(a) > 7 else 0.5; cy = float(a[8]) if len(a) > 8 else 0.8
    maxw = float(a[9]) if len(a) > 9 else 0.9; deg = float(a[10]) if len(a) > 10 else 5
    font = FONTS[a[11]] if len(a) > 11 else FONTS["bhs"]
    im = picture(src, sec, x0, y0, hh); red_text(im, text, cx, cy, maxw, deg, font)
    im.save(out, quality=95); print(out)
