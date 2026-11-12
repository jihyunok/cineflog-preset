# -*- coding: utf-8 -*-
"""다시나레 일본어판 썸네일 — 일본 벤치 推しシネマ 꼴(일본어판/thumb_oshi.py): 밝은 인물 한 컷 · 왼쪽 위 하늘색 꼬리표 · 왼쪽 아래 짧은 한마디(흰 글씨+그림자). 다른 글자 없음.
문구는 제브(소재거르기) 위 2개. 컷은 th/c/NN.png(확대 구역) 중 밝기 70 넘는 것(10-05 「어두운걸로 만들지마」).
사용: python thumb_ja.py [이름...] → D:/cine_work/redub_X_ja/th/j1.jpg·j2.jpg"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
FW = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/NotoSansJP-Bold.ttf")
FL = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/NotoSansJP-Black.ttf")
def make(src, out, word, label):
    im = Image.open(src).convert("RGB").resize((1280, 720))
    im = ImageEnhance.Brightness(im).enhance(1.15); im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.15); im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2))
    d = ImageDraw.Draw(im); size = 150
    while d.textlength(word, font=ImageFont.truetype(FW, size)) > 1190: size -= 8
    f = ImageFont.truetype(FW, size); x, y = 45, 720 - 50 - size
    sh = Image.new("RGBA", (1280, 720), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 6, y + 8), word, font=f, fill=(0, 0, 0, 170))
    im = Image.alpha_composite(im.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(8))).convert("RGB")
    d = ImageDraw.Draw(im); d.text((x, y), word, font=f, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    d.text((45, 18), label, font=ImageFont.truetype(FL, 78), fill=(0, 168, 225), stroke_width=3, stroke_fill=(0, 0, 0))
    im.save(out, quality=94)
K = "韓国ドラマ"
PICKS = {   # 이름: [(컷, 한마디, 제브)], 꼬리표
    "woo": ([("18", "新人の逆転劇"), ("12", "まさかの結末")], K),          # 0.79 · 0.70
    "evil": ([("15", "完璧な夫の正体"), ("04", "夫が殺人犯…？")], K),      # 0.80 · 0.75
    "mask": ([("01", "10年前の罪"), ("16", "親友の裏切り")], K),           # 0.72 · 0.70
    "sun": ([("03", "命をかけた愛"), ("01", "涙の結末…")], K),             # 0.75 · 0.70
    "happy": ([("10", "全てを失った女"), ("15", "親友の裏切り")], K),      # 0.73 · 0.71
    "siren": ([("09", "魔女の正体"), ("14", "保険金殺人…？")], K),         # 0.75 · 0.73
    "moon": ([("19", "正体を隠した女"), ("06", "記憶喪失…")], K),          # 0.76 · 0.70
    "love": ([("16", "90年代の名作"), ("07", "伝説の月9")], "名作ドラマ"),  # 0.78 · 0.77
    "재혼황후": ([("14", "皇帝の裏切り"), ("01", "運命の白い鳥")], K),      # 0.86 · 0.86 (11-12 아랍어 요약 채널 → 일본어판 시험)
}
if __name__ == "__main__":
    for s in (sys.argv[1:] or PICKS):
        picks, label = PICKS[s]; o = f"D:/cine_work/redub_{s}_ja/th"; os.makedirs(o, exist_ok=True)
        for k, (c, w) in enumerate(picks, 1): make(f"D:/cine_work/redub_{s}/th/c/{c}.png", f"{o}/j{k}.jpg", w, label)
        print("thumb", s)
