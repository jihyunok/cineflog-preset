# 11-01 친애하는 X(드라마상점)·메스를 든 사냥꾼(드라마라톤) 썸네일 — 원본 채널 스타일. 문구는 제브(소재거르기) 상위 4개.
# 드라마상점: 아래 큰 초록 「결말까지 한번에 몰아보기」 + 왼쪽 위 빨간 문구 / 드라마라톤: 위 초록 (문구) + 아래 큰 빨간 「결말까지 몰아보기」
import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
FD = "C:/Users/uere/AppData/Local/Microsoft/Windows/Fonts/"
def base(src, cx, cy, zoom):
    im = Image.open(src).convert("RGB"); W, H = im.size; ch = H / zoom; cw = ch * 16 / 9
    x0 = max(0, min(W - cw, cx * W - cw / 2)); y0 = max(0, min(H - ch, cy * H - ch / 2))
    im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((1280, 720), Image.LANCZOS)
    for E, v in ((ImageEnhance.Brightness, 1.12), (ImageEnhance.Contrast, 1.12), (ImageEnhance.Color, 1.12), (ImageEnhance.Sharpness, 1.5)): im = E(im).enhance(v)
    return im, ImageDraw.Draw(im)
def store(src, out, cx, cy, zoom, top):
    im, d = base(src, cx, cy, zoom)
    f = ImageFont.truetype("C:/Windows/Fonts/BlackHanSans-Regular.ttf", 104); t = "결말까지 한번에 몰아보기"; w = d.textlength(t, font=f)
    d.text(((1280 - w) / 2, 575), t, font=f, fill=(60, 255, 40), stroke_width=8, stroke_fill=(0, 0, 0))
    f2 = ImageFont.truetype("C:/Windows/Fonts/BlackHanSans-Regular.ttf", 72); d.text((120, 40), top, font=f2, fill=(255, 25, 25), stroke_width=7, stroke_fill=(0, 0, 0))
    im.save(out, quality=93)
def marathon(src, out, cx, cy, zoom, top):
    im, d = base(src, cx, cy, zoom)
    f2 = ImageFont.truetype(FD + "Jalnan2TTF.ttf", 70); t = f"({top})"; w = d.textlength(t, font=f2)
    d.text(((1280 - w) / 2, 30), t, font=f2, fill=(40, 255, 40), stroke_width=10, stroke_fill=(0, 0, 0))
    f = ImageFont.truetype(FD + "Cafe24Dangdanghae.ttf", 130); t = "결말까지 몰아보기"; w = d.textlength(t, font=f)
    d.text(((1280 - w) / 2, 545), t, font=f, fill=(255, 20, 20), stroke_width=12, stroke_fill=(0, 0, 0))
    im.save(out, quality=93)
if __name__ == "__main__":
    D = "D:/cine_work/redub_dearx/th/"
    store(D + "f4125.png", D + "n1.jpg", .62, .46, 1.4, "미소 뒤에 숨긴 잔인한 본색")
    store(D + "f3075.png", D + "n2.jpg", .55, .46, 1.4, "천사의 얼굴을 한 악마")
    store(D + "f1425.png", D + "n3.jpg", .5, .46, 1.4, "가장 위험한 여자")
    store(D + "f5475.png", D + "n4.jpg", .33, .46, 1.4, "모두를 파멸시킨 소시오패스")
    M = "D:/cine_work/redub_mes/th/"
    marathon(M + "f675.png", M + "n1.jpg", .5, .45, 1.5, "아빠를 사냥하는 부검의")
    marathon(M + "f1725.png", M + "n2.jpg", .7, .45, 1.5, "아빠가 연쇄살인마였다")
    marathon(M + "f2775.png", M + "n3.jpg", .3, .45, 1.5, "연쇄살인마의 딸")
    marathon(M + "f4725.png", M + "n4.jpg", .62, .45, 1.5, "천재 부검의의 복수")
