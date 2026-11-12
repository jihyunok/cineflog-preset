# -*- coding: utf-8 -*-
"""11-08 썸네일 글자 = 최근 떡상 영화리뷰 꼴 (사용자 「인물은 됬는데 텍스트를 좀 바꿔. 최근 떡상한 영화보고 바꿔」)
분석(이번 달 조회수 상위 16개, 무비트립·지무비·드림텔러·카랑·리뷰한사발 등):
 · 아래 한 줄 = 인물 대사·반응처럼 짧게(「건드리지 말랬지」「반드시 복수해줄게」「이거 겁나 재밌음!!」「인간인가 기계인가」), 아주 크게, 흰+빨강 두 색, 기울임 거의 없음
 · 인물 머리 위에 작은 괄호 별명표(「(싸움의 신)」「(전투력 1위 전학생)」「레전드 요원 1위」) — 초록·노랑, 검은 테두리
 · 위 가운데 붓글씨 문장은 거의 없음
사용: python thumb_label.py 그림 x0 y0 h "아래 흰말" "아래 빨간말" 출력.jpg "x비율,y비율,색,(별명)" ...
  색 = g(초록)·y(노랑)·w(흰)  · 그림은 png/jpg(얼굴 반반 합성 duo.py 결과 등), h=0 이면 통째"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from thumb_quote import picture, fit, JALNAN, W, H, WHITE, RED
from PIL import Image
COL = {"g": (70, 255, 90), "y": (255, 228, 40), "w": (255, 255, 255)}

def make(src, x0, y0, hh, white, red, out, labels):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "v9"))
    from yt_safe import die_if_bad
    die_if_bad(white, red, *[l.split(",", 3)[3] for l in labels], where="썸네일")
    im = picture(src, 0, x0, y0, hh).convert("RGBA")
    for l in labels:
        fx, fy, c, t = l.split(",", 3)
        q = fit([(t, COL.get(c, COL["g"]))], JALNAN, int(W * 0.47), int(H * 0.115), 0.12)
        x = int(float(fx) * W - q.width / 2); x = max(6, min(W - q.width - 6, x))
        im.alpha_composite(q, (x, int(float(fy) * H)))
    parts = [(white + " ", WHITE), (red, RED)] if white else [(red, RED)]
    b = fit(parts, JALNAN, int(W * 0.96), int(H * 0.27), 0.08, shear=0.05)
    im.alpha_composite(b, (int(W / 2 - b.width / 2), H - b.height - int(H * 0.02)))
    im.convert("RGB").save(out, quality=95); print(out)

if __name__ == "__main__":
    a = sys.argv[1:]
    make(a[0], int(a[1]), int(a[2]), int(a[3]), a[4], a[5], a[6], a[7:])
