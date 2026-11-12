# -*- coding: utf-8 -*-
"""post2.py 뒤(11-12 31v2) — 실제 녹음 길이로 plan 「자리 없음」 8줄 손질. 글 줄임 4줄(다시 녹음) · 구간 넓힘 4줄.
판단 근거: 녹음 문장 길이(narr/nNNN.json) + 앞뒤 조각 3초 간격(windows.json) + 컷 설명(room.py)·프레임(_seg/s_k3.jpg)."""
import json
WK = r"D:\cine_work\ep31v2_잭리처"
R = [  # (옛 줄 앞부분 그대로, 새 줄, 새 EN 또는 None)
 ('("N", "체포된 용의자는 끝내 입을 열지 않았죠. 노트엔 잭 리처라는 이름뿐.", [(590.5, 593.8), (584.0, 586.3)]',
  '("N", "체포된 용의자는 끝내 입을 열지 않았죠. 노트엔 잭 리처.", [(590.5, 593.8), (584.0, 586.3)]',
  "The arrested suspect never says a word. On his notepad: Jack Reacher."),   # 프레임 봄 s_k3.jpg: 노트 GET JACK REACHER 는 584.0~586.3 2.3초뿐(586.5 부터 에머슨) — 녹음 2.32초가 안 들어감
 ('제임스 바.", [(434.1, 437.5), (445.0, 448.8)]',
  '제임스 바.", [(434.1, 437.5), [(442.2, 445.0), (445.1, 448.9)]]', None),   # 둘째 문장 2.8초 → 조각 둘: 컷 설명 442.2 지문 대조 진행·443.0 MATCH FOUND / 445.1 Barr, J. 이름 화면
 ('("N", "헬렌은 바의 사형만은 막겠다고 하죠.", [(910.3, 914.1)]',
  '("N", "헬렌은 사형만은 막겠다고 하죠.", [(910.3, 914.1)]', "Helen says she will at least stop the death penalty."),   # 2.64초 → 조각 둘이 돼 말하는 헬렌 컷(910.1~914.1)에 안 들어감 — 줄임
 ('("N", "눈을 감고 바를 떠올리는 리처.", [(977.9, 980.8)]',
  '("N", "리처는 지그시 눈을 감습니다.", [(977.9, 980.3)]', "Reacher slowly closes his eyes."),   # 다음 대사 983.3 −3초 = 980.3 까지 2.4초뿐 — 줄임(작업자가 본 눈 감은 리처 컷)
 ('("N", "청소부 리타는 늘 아들을 바래다줬죠.", [(2331.1, 2336.8)]',
  '("N", "청소부 리타는 늘 아들을 바래다줬죠.", [[(2331.1, 2334.5), (2339.8, 2345.5)]]', None),   # 조각 둘: 컷 설명 2330.6 함께 걷는 여자와 소년 / 2339.7 계단을 내려오는 여자와 책가방 소년(2336.9 차 안 헬렌은 건너뜀)
 ('("N", "모든 일의 배후, 더 젝입니다.", [(2780.9, 2783.4)]',
  '("N", "모든 일의 배후, 더 젝입니다.", [(2780.85, 2783.6)]', None),   # 프레임 봄 s_k164.jpg: 더 젝 얼굴은 2780.9~2783.4(앞 2779.5~2780.5 는 다른 남자 옆얼굴), 2789.9~ 는 다음 대사 2794.7 과 3초 간격에 걸림
 ('[[(5925.2, 5928.3), (5928.4, 5932.4)], (5937.4, 5941.4)',
  '[[(5925.2, 5928.3), (5928.4, 5933.0)], (5937.4, 5941.4)', None),   # 첫 문장 둘째 조각이 0.1초 모자람 — 5933.1 충격기 공격 컷 앞까지
 ('("N", "그 시각 더 젝은 헬렌을 마주하고 있죠.", [(6313.9, 6319.6)]',
  '("N", "더 젝이 헬렌을 마주합니다.", [(6313.9, 6316.9)]', "The Zec faces Helen."),   # 앞 대사 6310.9+3 ~ 다음 대사 6319.9−3 = 3.0초뿐 — 줄임(프레임 봄 6314.1·6315.4 헬렌 어깨 너머 더 젝)
]
s = open(f"{WK}/script.py", encoding="utf-8").read()
en = json.load(open(f"{WK}/narr_en.json", encoding="utf-8")); em = json.load(open(f"{WK}/emph.json", encoding="utf-8"))
ns0 = {}; exec(s, ns0); T0 = [x[1] for x in ns0["S"] if x[0] == "N"]
t2e = {t: en.get(str(i + 1), "") for i, t in enumerate(T0)}; t2m = {t: em["n"].get(str(i + 1)) for i, t in enumerate(T0)}
for a, b, e in R:
    assert s.count(a) == 1, a[:50]
    s = s.replace(a, b)
ns = {}; exec(s, ns); NT = [x[1] for x in ns["S"] if x[0] == "N"]
for (t_old, t_new) in zip(T0, NT):
    if t_old != t_new:
        e = next((e for a, b, e in R if t_new in b), None)
        t2e[t_new] = e or t2e.get(t_old, ""); t2m[t_new] = t2m.get(t_old)
open(f"{WK}/script.py", "w", encoding="utf-8").write(s)
json.dump({str(i + 1): t2e.get(t, "") for i, t in enumerate(NT)}, open(f"{WK}/narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
em["n"] = {str(i + 1): t2m[t] for i, t in enumerate(NT) if t2m.get(t) and t2m[t][0] in t}
json.dump(em, open(f"{WK}/emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", len(NT), "· 바뀐 글", sum(a != b for a, b in zip(T0, NT)), "· 영어 없음", [t[:20] for t in NT if not t2e.get(t)], "· 강조", len(em["n"]))
