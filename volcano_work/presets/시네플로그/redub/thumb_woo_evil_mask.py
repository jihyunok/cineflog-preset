# 11-01 우영우·가면의 여왕(드라마라톤 새 스타일)·악의 꽃(무비바이브) 썸네일 — 원본 채널 스타일. 문구는 제브(소재거르기) 상위 4개.
# 드라마라톤: 위 「결말까지 몰아보기」(당당해) + 아래 아주 큰 빨간 문구(검은 테) / 무비바이브: 왼쪽 위 빨간 문구 + 아래 노란 「결말까지 한방에 몰아보기」
from PIL import ImageFont
from thumb_dearx_mes import base, FD
BH = "C:/Windows/Fonts/BlackHanSans-Regular.ttf"
def fit(d, t, path, size, maxw):
    while True:
        f = ImageFont.truetype(path, size)
        if d.textlength(t, font=f) <= maxw or size < 40: return f
        size -= 4
def marathon2(src, out, cx, cy, zoom, hook, two_color=False):
    im, d = base(src, cx, cy, zoom)
    f = ImageFont.truetype(FD + "Cafe24Dangdanghae.ttf", 92)
    if two_color:                       # 가면의 여왕: 「결말까지」 노랑 + 「몰아보기」 빨강
        a, b = "결말까지 ", "몰아보기"; wa = d.textlength(a, font=f); x = (1280 - wa - d.textlength(b, font=f)) / 2
        d.text((x, 18), a, font=f, fill=(255, 230, 30), stroke_width=9, stroke_fill=(0, 0, 0))
        d.text((x + wa, 18), b, font=f, fill=(255, 25, 25), stroke_width=9, stroke_fill=(0, 0, 0))
    else:
        t = "결말까지 몰아보기"; w = d.textlength(t, font=f)
        d.text(((1280 - w) / 2, 18), t, font=f, fill=(255, 230, 30), stroke_width=9, stroke_fill=(0, 0, 0))
    f2 = fit(d, hook, BH, 150, 1220); w = d.textlength(hook, font=f2); h = f2.getbbox(hook)[3]
    d.text(((1280 - w) / 2, 700 - h - 10), hook, font=f2, fill=(255, 20, 20), stroke_width=13, stroke_fill=(0, 0, 0))
    im.save(out, quality=93)
def moviebibe(src, out, cx, cy, zoom, hook):
    im, d = base(src, cx, cy, zoom)
    f = ImageFont.truetype(FD + "GmarketSansTTFBold.ttf", 64)
    d.text((40, 30), hook, font=f, fill=(240, 20, 20), stroke_width=5, stroke_fill=(0, 0, 0))
    f2 = ImageFont.truetype(FD + "GmarketSansTTFBold.ttf", 80); t = "결말까지 한방에 몰아보기"; w = d.textlength(t, font=f2)
    d.text(((1280 - w) / 2, 590), t, font=f2, fill=(255, 225, 20), stroke_width=7, stroke_fill=(0, 0, 0))
    im.save(out, quality=93)
if __name__ == "__main__":   # th/c/NN.png = zoom_args 의 확대 구역(옛 자막 없는 곳)을 1280x720 으로 뽑은 것
    for show, fn, picks, extra in (
        ("woo", marathon2, [("01", "모두가 무시한 신입의 반전"), ("03", "아무도 몰랐던 출생의 비밀"), ("12", "자폐 천재 변호사의 첫 재판"), ("18", "법정을 뒤집은 천재")], ()),
        ("evil", moviebibe, [("09", "남편이 연쇄살인마의 아들이었다"), ("15", "형사 아내가 쫓던 범인은 남편"), ("04", "완벽한 남편의 소름 돋는 비밀"), ("19", "사랑을 연기한 남자")], ()),
        ("mask", marathon2, [("01", "가면 속 진짜 범인"), ("16", "10년 만에 돌아온 복수"), ("07", "친구 넷이 숨긴 살인"), ("18", "우정을 배신한 친구")], (True,))):
        D = f"D:/cine_work/redub_{show}/th/"
        for k, (c, hook) in enumerate(picks, 1): fn(D + f"c/{c}.png", D + f"n{k}.jpg", .5, .5, 1.0, hook, *extra)
