# -*- coding: utf-8 -*-
"""시네플로그 썸네일 — 얼굴 크게 + 위 작은 빨간 붓글씨 + 아래 흰·빨강 아주 큰 기울인 글자
(10-16 사용자 참고 캡처 리암 니슨 「-모조리 죽여줄게..- / 진짜 존X잘싸움」 "이런느낌으로" → "진짜존x 재밌음 이렇게 글자 쓰고 위에 작은글자로 에어포스원 추락?").
주인공 얼굴을 화면 가운데 크게, 위에 작은 「-…..-」 빨간 붓글씨(검은 테두리), 아래 한 줄 = 흰 앞말 + 빨간 뒷말
(잘난체, 오른쪽으로 기울임, 검은 테두리 + 그림자, 화면 폭 가득). 그림은 밝게("섬네일이미지는 밝은걸로해") — 밝은 장면을 고르고 감마로 어두운 쪽만 들어 올림·채도·선명하게, 가장자리만 살짝 어둡게.
사용: python thumb_quote.py 그림(png/jpg/mp4) 초 x0 y0 h "위 글" "아래 흰말" "아래 빨간말" 출력.jpg
  x0 y0 h = 원본에서 16:9 로 자를 왼쪽·위·높이(h=0 이면 통째)
01 헤즈 오브 스테이트(원본 영화가 지워져 작업 폴더 clips 에서 뽑음): 「-에어포스원 추락..-」 / 「진짜 존X재밌음」"""
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageChops
W, H = 1280, 720
JALNAN = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/Jalnan2TTF.ttf")
BHS = r"C:/Windows/Fonts/BlackHanSans-Regular.ttf"
BHS = BHS if os.path.exists(BHS) else os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/BlackHanSans-Regular.ttf")
JALNAN = JALNAN if os.path.exists(JALNAN) else BHS   # 10-19 잘난체 없는 PC → 블랙한산스
BRUSH = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/EastSeaDokdo-Regular.ttf")
RED, WHITE = (236, 22, 22), (255, 255, 255)
DD = ImageDraw.Draw(Image.new("L", (8, 8)))

def picture(src, sec, x0, y0, hh):
    if src.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        im = Image.open(src).convert("RGB")
    else:
        tmp = f"_q_{os.getpid()}.png"   # 10-17 여러 장 동시에 돌리면 같은 _q.png 를 서로 지워 깨졌다
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(sec), "-i", src, "-frames:v", "1", tmp], check=True)
        im = Image.open(tmp).convert("RGB"); os.remove(tmp)
    if hh > 0:
        ww = round(hh * 16 / 9); im = im.crop((x0, y0, x0 + ww, y0 + hh))
    im = im.resize((W, H), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=0.5)
    im = im.point(lambda p: int(255 * (p / 255) ** 0.85))                        # 밝게: 어두운 쪽을 들어 올림(허옇게 날리지 않게 감마로)
    im = ImageEnhance.Brightness(im).enhance(1.06); im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.22)
    im = im.filter(ImageFilter.UnsharpMask(radius=8, percent=30, threshold=0))   # 결 살리기
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=2))
    v = Image.radial_gradient("L").resize((W, H)).point(lambda p: 255 - int(min(255, max(0, (p - 110) * 1.6)) * 0.3))  # 가장자리만 살짝
    return ImageChops.multiply(im, Image.merge("RGB", (v, v, v)))

def box(parts, font, sz, e):
    f = ImageFont.truetype(font, sz); bb = DD.textbbox((0, 0), "".join(t for t, _ in parts), font=f, stroke_width=e)
    return f, bb, bb[2] - bb[0], bb[3] - bb[1]

def outlined(parts, font, sz, e, shear=0.0):
    """parts = [(글, 색)…] 를 한 줄로, 검은 테두리(stroke) + 아래로 번진 그림자, shear 만큼 오른쪽으로 기울임(RGBA)."""
    f, bb, tw, th = box(parts, font, sz, e); pad = 24 + int(th * abs(shear)); CW, CH = tw + pad * 2, th + 48
    lay = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); sh = Image.new("L", (CW, CH), 0)
    ld, sd = ImageDraw.Draw(lay), ImageDraw.Draw(sh); x = pad - bb[0]; y = 24 - bb[1]
    for t, c in parts:
        sd.text((x, y), t, font=f, fill=255, stroke_width=e, stroke_fill=255)
        ld.text((x, y), t, font=f, fill=c, stroke_width=e, stroke_fill=(0, 0, 0))
        x += DD.textlength(t, font=f)
    out = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    out.paste((0, 0, 0, 200), (7, 9), sh.filter(ImageFilter.GaussianBlur(7)).crop((0, 0, CW - 7, CH - 9)))
    out = Image.alpha_composite(out, lay)
    if shear:
        out = out.transform(out.size, Image.AFFINE, (1, shear, -shear * CH / 2, 0, 1, 0), resample=Image.BICUBIC)
    return out.crop(out.getbbox())

def fit(parts, font, maxw, maxh, edge_ratio, shear=0.0):
    sz = 320
    while sz > 30:
        _, _, tw, th = box(parts, font, sz, max(3, int(sz * edge_ratio)))
        if tw + th * abs(shear) + 20 <= maxw and th + 20 <= maxh: break
        sz -= 2
    return outlined(parts, font, sz, max(3, int(sz * edge_ratio)), shear)

def make(src, sec, x0, y0, hh, top, white, red, out):
    im = picture(src, sec, x0, y0, hh).convert("RGBA")
    if top:                                              # 위: 작은 「-…..-」 빨간 붓글씨
        q = fit([(f"-{top}..-", RED)], BRUSH, int(W * 0.48), int(H * 0.15), 0.1)
        im.alpha_composite(q, (int(W / 2 - q.width / 2), int(H * 0.035)))
    parts = [(white + " ", WHITE), (red, RED)] if white else [(red, RED)]
    b = fit(parts, JALNAN, int(W * 0.95), int(H * 0.26), 0.075, shear=0.16)   # 아래: 흰 앞말 + 빨간 뒷말, 기울임
    im.alpha_composite(b, (int(W / 2 - b.width / 2), H - b.height - int(H * 0.025)))
    im.convert("RGB").save(out, quality=95); print(out)

if __name__ == "__main__":
    a = sys.argv[1:]
    make(a[0], float(a[1]), int(a[2]), int(a[3]), int(a[4]), a[5], a[6], a[7], a[8])
