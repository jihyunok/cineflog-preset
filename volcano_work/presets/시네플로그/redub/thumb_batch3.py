# 11-01 나의 해피엔드·유별나! 문셰프(우리드라마)·세이렌(행드리)·러브 제너레이션(기묘한 김선생)·미스터 션샤인(드라마야) 썸네일 — 원본 채널 스타일. 문구는 제브(소재거르기).
# 프레임은 th/c/NN.png (zoom_args 확대 구역 = 옛 자막 없는 곳, 1280x720)
import sys
from PIL import ImageFont, ImageDraw
from thumb_dearx_mes import base, FD
from thumb_woo_evil_mask import fit, BH
DD = FD + "Cafe24Dangdanghae.ttf"
def happy(src, out, hook):      # 우리드라마: 왼쪽 흰 두 줄 문구 + 아래 큰 빨간 「결말까지 몰아보기」
    im, d = base(src, .5, .5, 1.0)
    f = ImageFont.truetype(BH, 84); y = 230
    for line in hook.split("\n"):
        d.text((50, y), line, font=f, fill=(255, 255, 255), stroke_width=9, stroke_fill=(0, 0, 0)); y += 100
    f2 = ImageFont.truetype(DD, 140); t = "결말까지 몰아보기"; w = d.textlength(t, font=f2)
    d.text(((1280 - w) / 2, 545), t, font=f2, fill=(255, 20, 20), stroke_width=13, stroke_fill=(0, 0, 0))
    im.save(out, quality=93)
def moon(src, out, hook):       # 우리드라마(문셰프): 위 초록 (문구) + 아래 큰 빨간 「결말까지 몰아보기」
    im, d = base(src, .5, .5, 1.0)
    f = ImageFont.truetype(FD + "Jalnan2TTF.ttf", 72); t = f"({hook})"; w = d.textlength(t, font=f)
    d.text(((1280 - w) / 2, 30), t, font=f, fill=(40, 255, 40), stroke_width=10, stroke_fill=(0, 0, 0))
    f2 = ImageFont.truetype(BH, 150); t = "결말까지 몰아보기"; w = d.textlength(t, font=f2)
    d.text(((1280 - w) / 2, 520), t, font=f2, fill=(255, 20, 20), stroke_width=13, stroke_fill=(0, 0, 0))
    im.save(out, quality=93)
def siren(src, out, hook):      # 행드리: 오른쪽 위 작은 문구 + 아래 노란 「결말까지 몰아보기」
    im, d = base(src, .5, .5, 1.0)
    f = ImageFont.truetype(FD + "Jalnan2TTF.ttf", 60); w = d.textlength(hook, font=f)
    d.text((1240 - w, 40), hook, font=f, fill=(255, 255, 60), stroke_width=8, stroke_fill=(0, 0, 0))
    f2 = ImageFont.truetype(DD, 130); t = "결말까지 몰아보기"; w = d.textlength(t, font=f2)
    d.text(((1280 - w) / 2, 555), t, font=f2, fill=(255, 225, 20), stroke_width=12, stroke_fill=(0, 0, 0))
    im.save(out, quality=93)
def love(src, out, hook):       # 기묘한 김선생: 분홍 테 + 오른쪽 빨간 「결말까지 2시간 몰아보기」 + 아래 흰 제목 + 위 문구
    im, d = base(src, .5, .5, 1.0)
    d.rectangle((0, 0, 1279, 719), outline=(255, 60, 140), width=22)
    f = ImageFont.truetype(BH, 74)
    for k, t in enumerate(("결말까지", "2시간", "몰아보기")):
        w = d.textlength(t, font=f); d.text((1230 - w, 50 + k * 88), t, font=f, fill=(255, 30, 30), stroke_width=7, stroke_fill=(255, 255, 255))
    f2 = ImageFont.truetype(BH, 120); t = "러브 제너레이션"; w = d.textlength(t, font=f2)
    d.text(((1280 - w) / 2, 560), t, font=f2, fill=(255, 255, 255), stroke_width=12, stroke_fill=(230, 20, 60))
    f3 = fit(d, hook, FD + "Jalnan2TTF.ttf", 60, 640); d.text((50, 50), hook, font=f3, fill=(255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0))
    im.save(out, quality=93)
def sun(src, out, hook):        # 드라마야(우아한 가와 같은 틀): 아래 노란 「결말까지 한 번에 몰아보기」 + 위 빨간 문구
    im, d = base(src, .5, .5, 1.0)
    f = ImageFont.truetype(DD, 96); t = "결말까지 한 번에 몰아보기"; w = d.textlength(t, font=f)
    d.text(((1280 - w) / 2, 575), t, font=f, fill=(255, 230, 30), stroke_width=9, stroke_fill=(0, 0, 0))
    f2 = fit(d, hook, DD, 84, 1200); w = d.textlength(hook, font=f2)
    d.text(((1280 - w) / 2, 28), hook, font=f2, fill=(240, 20, 20), stroke_width=8, stroke_fill=(0, 0, 0))
    im.save(out, quality=93)
PICKS = {
    "happy": (happy, [("15", "모든 걸 가진\n여자의 추락"), ("14", "20년 지기\n절친의 배신"), ("10", "남편과\n절친의 불륜"), ("07", "완벽한 인생이\n무너졌다")]),
    "siren": (siren, [("04", "보험금을 노리는 여자"), ("09", "사랑하면 죽는 여자"), ("16", "그녀를 사랑한 남자들의 최후"), ("03", "전 남친 3명이 모두 죽었다")]),
    "moon": (moon, [("06", "거식증 디자이너를 살린 셰프의 요리"), ("19", "가족을 잃은 스타 셰프의 로맨스"), ("01", "기억 잃은 톱 디자이너와 스타 셰프"), ("04", "기억상실 디자이너를 데려온 셰프")]),   # 기억 잃는 건 셰프 아니라 디자이너(대본 확인)
    "love": (love, [("03", "90년대 일본 최고의 사랑 이야기"), ("07", "기무라 타쿠야 전설의 로맨스"), ("14", "형의 여자를 사랑했다"), ("16", "원조 일드 로맨스의 정석")]),
    "sun": (sun, [("03", "조선을 버린 남자의 귀환"), ("01", "이병헌 김태리 인생 드라마"), ("02", "노비의 아들, 미국 군인이 되다"), ("10", "총을 든 양반집 아가씨")]),
}
if __name__ == "__main__":
    for show in (sys.argv[1:] or PICKS):
        fn, picks = PICKS[show]; D = f"D:/cine_work/redub_{show}/th/"
        for k, (c, hook) in enumerate(picks, 1): fn(D + f"c/{c}.png", D + f"n{k}.jpg", hook)
