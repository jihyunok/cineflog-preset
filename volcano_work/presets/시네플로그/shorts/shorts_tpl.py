# -*- coding: utf-8 -*-
"""영화 리뷰 쇼츠 템플릿(다른 PC 「대작」에서 10-20 가져옴) — 10-19 사용자 "쇼츠 템플릿이야.이미지 넣고 하나 만들어봐" · "템플릿은 위아래만 쓰고 양쪽 테두리는 넣지마."
템플릿(shorts/쇼츠템플릿_명작영화.jpg 1536x2752)의 위 제목 띠(0~603)·아래 객석 띠(2150~)만 1080 폭으로 쓰고, 가운데 1080x1072 는 영화 장면을 가로 꽉 차게(양옆 필름 테두리 없음).
자막 = Pretendard Black 70 흰 글씨·검은 테두리 7, 영상 자리 아래쪽. 견본: 사진 1장 + 영상(원본 소리 — 실제 쇼츠는 나레·반전·3초 규칙).
★10-19 "템플릿에서 글자만 지운 판을 만들어" → 쇼츠템플릿_명작영화_글자없음.jpg(제목 자리 y212~562 를 위·아래 커튼 색으로 이어 메움) + 편마다 제목 두 줄을
  원래 꼴(윗줄 크림·아랫줄 금색, Pretendard Black, 아래 그림자)로 써 넣는다. 제목을 주면 글자없음 판을 쓴다.
★10-20 build_shorts.py 가 make_frame() 을 불러 쓴다(틀·제목·「대작」 한 곳).
사용: python shorts_tpl.py 템플릿.jpg 원본영상 사진초 영상시작초 영상길이 출력폴더 "자막" ["제목 윗줄" "제목 아랫줄"]"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
TOP_END, BOT_START = 604, 2150            # 템플릿 1536x2752: 화면 검은 테두리가 604 에서 시작, 2148 에서 끝
FONT = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/Pretendard-Black.otf")


def make_frame(tpl=None, title=None, brand="CINEFLOG", wm=None):
    """템플릿 위·아래 띠 + 제목 두 줄 + 오른쪽 위 채널 글자(brand) 또는 워터마크 그림(wm) → (RGBA 1080x1920, 영상 자리 위 y, 아래 y)
    brand·wm 은 롱폼과 같은 ep.json "brand"·"brand_png"(build_shorts 가 넘김). 이 PC 기본 CINEFLOG 글자 — 다른 PC 는 「대작」 그림."""
    if title: tpl = os.path.join(HERE, "쇼츠템플릿_명작영화_글자없음.jpg")
    tp = Image.open(tpl or os.path.join(HERE, "쇼츠템플릿_명작영화.jpg")).convert("RGB"); s = W / tp.width
    top = tp.crop((0, 0, tp.width, TOP_END)).resize((W, round(TOP_END * s)), Image.LANCZOS)
    bot = tp.crop((0, BOT_START, tp.width, tp.height)).resize((W, round((tp.height - BOT_START) * s)), Image.LANCZOS)
    my0, my1 = top.height, H - bot.height          # 가운데 영상 자리
    if title:   # 원래 템플릿 실측(1080 폭): 윗줄 y161~261 크림 · 아랫줄 y281~381 금색 · 아래쪽 검은 그림자
        for txt, cy, col in ((title[0], 211, (243, 233, 210)), (title[1], 331, (247, 195, 92))):
            sz = 112
            while ImageFont.truetype(FONT, sz).getlength(txt) > 1000: sz -= 2
            fo = ImageFont.truetype(FONT, sz); tw = fo.getlength(txt); x = (W - tw) / 2; y = cy - sz * 0.62
            sh = Image.new("RGBA", top.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 4, y + 9), txt, font=fo, fill=(0, 0, 0, 200))
            top = Image.alpha_composite(top.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(6)))
            ImageDraw.Draw(top).text((x, y), txt, font=fo, fill=col)
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0)); frame.paste(top, (0, 0)); frame.paste(bot, (0, my1))
    # ★10-19 "워터마크는 우측상단에 롱,숏 둘다 넣는거 알지?" — 롱폼 TOP 줄과 같은 꼴(Noto Sans KR Black · 회색 B5B5B5 · 검은 테두리)을 영상 자리 오른쪽 위에
    #   10-19 "대작 워터마크 지금보이는것보다 더 크게 만들어" → 58 → 88
    #   ★10-20 "그리고 대작 워터마크 무드킹처럼 만들어" → brand/대작_워터마크.png(롱폼과 같은 그림), 없으면 옛 글자
    if wm and not os.path.isabs(wm): wm = os.path.join(HERE, "..", "brand", wm)
    if wm and os.path.exists(wm):
        im = Image.open(wm).convert("RGBA"); frame.alpha_composite(im, (W - 44 - im.width, my0 + 34))   # 10-20 "아래 왼쪽으로 조금 옮겨"
    else:
        bf = ImageFont.truetype(os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/NotoSansKR-Black.ttf"), 88)
        ImageDraw.Draw(frame).text((W - 24 - bf.getlength(brand), my0 + 10), brand, font=bf, fill=(181, 181, 181), stroke_width=4, stroke_fill="black")
    return frame, my0, my1


if __name__ == "__main__":
    TPL, SRC, T_IMG, T0, DUR, OUT, CAP = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6], sys.argv[7]
    TITLE = sys.argv[8:10] if len(sys.argv) > 9 else None
    os.makedirs(OUT, exist_ok=True)
    frame, MY0, MY1 = make_frame(TPL, TITLE); MH = MY1 - MY0
    frame.save(f"{OUT}/_frame.png")
    # 자막: 흰 굵은 글씨 + 검은 테두리, 영상 자리 아래쪽
    f = ImageFont.truetype(FONT, 70); cap = Image.new("RGBA", (W, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(cap)
    tw = d.textlength(CAP, font=f); d.text(((W - tw) / 2, 30), CAP, font=f, fill="white", stroke_width=7, stroke_fill="black")
    cap.save(f"{OUT}/_cap.png"); CY = MY1 - 175
    vf = f"scale=-2:{MH},crop={W}:{MH}"
    # 사진
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{T_IMG}", "-i", SRC, "-i", f"{OUT}/_frame.png", "-i", f"{OUT}/_cap.png", "-frames:v", "1", "-filter_complex",
                    f"[0:v]{vf},pad={W}:{H}:0:{MY0}:black[a];[a][1:v]overlay=0:0[b];[b][2:v]overlay=0:{CY}", f"{OUT}/쇼츠견본_사진.png"], check=True)
    # 10초 영상(원본 소리)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{T0}", "-t", f"{DUR}", "-i", SRC, "-loop", "1", "-i", f"{OUT}/_frame.png", "-loop", "1", "-i", f"{OUT}/_cap.png", "-filter_complex",
                    f"[0:v]{vf},pad={W}:{H}:0:{MY0}:black[a];[a][1:v]overlay=0:0:shortest=1[b];[b][2:v]overlay=0:{CY}:shortest=1,format=yuv420p[o]",
                    "-map", "[o]", "-map", "0:a:0", "-t", f"{DUR}", "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", f"{OUT}/쇼츠견본_10초.mp4"], check=True)
    print("영상 자리", W, "x", MH, "· 위", MY0, "· 아래", H - MY1, "· 자막 y", CY)
