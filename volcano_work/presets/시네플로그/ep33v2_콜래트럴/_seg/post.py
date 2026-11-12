# -*- coding: utf-8 -*-
"""merge.py 뒤 본체 손질(11-07 33v2) — 관문 ⑮(앞 5분 나레 없이 대사 5줄+) 두 곳. merge 를 다시 돌리면 이것도 다시."""
import json
WK = r"D:\cine_work\ep33v2_콜래트럴"
P = [
 ('("D", [439], "살인을 도울 순 없다고요", {"noflip": True}),\n("D", [445, 446], "이해를 못 하는군요 / 농담이 아니에요 / 난 이런 일 정말 못 해요"),',
  '("D", [439], "살인을 도울 순 없다고요", {"noflip": True}),\n("N", "빈센트는 눈 하나 깜짝하지 않죠.", 1525.0, 1531.5, {"cont": True}),   # 11-07 본체: ⑮ 대사 7줄 연속 끊기 — 앞 대사 바로 뒤 빈센트 클로즈업(1527.1 컷 설명) 이어 감\n("D", [445, 446], "이해를 못 하는군요 / 농담이 아니에요 / 난 이런 일 정말 못 해요", {"noflip": True}),   # 11-07 이음 나레 앞뒤 같은 반전(cont)'),
 ('("A", 1682.8, 1685.4, 2.3, {"noflip": True}),   # 빈 구간 채움(말소리 없는 곳 10-21)\n("D", [534, 535]',
  '("N", "경찰은 면허증을 확인하며 택시 안을 살피는데요.", [(1675.0, 1693.0)], {"sent": True}),   # 11-07 본체: ⑮ 검문 대사 6줄 연속 끊기 — A 1682.8 대신, 1675.5 몸을 숙인 경찰을 올려다보는 맥스·1679.5 깨진 택시 위 경찰(컷 설명)\n("D", [534, 535]'),
]
P += [
 ("근사한 차라고요. 맥스는 애니의", "근사한 차라는 거죠. 맥스는 애니의"),
 ("살아남으면 꼭 하라고요.", "살아남으면 꼭 하라는 거죠."),
 ('("N", "당신은 사람이 아니라고요.", [(5328.0, 5332.3)]', '("N", "사람도 아니라며 쏘아붙이는 맥스.", [(5328.0, 5332.3)]'),
 ("[(5161.8, 5164.2)]", "[(5161.7, 5164.3)]"),
 ("깨진 앞 유리 탓에 경찰에 붙잡힌 택시.", "유리 깨진 택시가 경찰에 걸립니다."),
]   # 11-07 본체: 「~고요」 금지 · 녹음 뒤 자리 없음 두 줄(구간 0.1초 넓힘 / 글 줄임)(텔레그램 「"~고요" 는 쓰지마」) — v1 에서 넘어온 「~라고요」 세 줄
EN = {"유리 깨진 택시가 경찰에 걸립니다.": "The cab with the broken windshield gets pulled over by the police.", "공항에 도착해도 내리기 싫을 만큼 근사한 차라는 거죠. 맥스는 애니의 옷차림과 가방만 보고, 그녀의 직업을 맞혀 보는데요.": "He says it will be a car so nice you won't want to get out even at the airport. Judging only by Annie's clothes and bag, Max tries to guess what she does for a living.", "빈센트는 맥스에게 애니에게 전화하라고 말합니다. 살아남으면 꼭 하라는 거죠.": "Vincent tells Max to call Annie. He says to be sure to do it if he survives.", "사람도 아니라며 쏘아붙이는 맥스.": "Max snaps that Vincent is not even human.", "빈센트는 눈 하나 깜짝하지 않죠.": "Vincent doesn't even blink.", "경찰은 면허증을 확인하며 택시 안을 살피는데요.": "The officer checks the license and peers around inside the cab."}
EMPH = {"사람도 아니라며 쏘아붙이는 맥스.": ["사람도 아니라며", "threat"], "경찰은 면허증을 확인하며 택시 안을 살피는데요.": ["택시 안을 살피는데요", "threat"]}
s = open(f"{WK}/script.py", encoding="utf-8").read()
for a, b in P:
    assert s.count(a) == 1, a[:40]; s = s.replace(a, b)
open(f"{WK}/script.py", "w", encoding="utf-8").write(s)
ns = {}; exec(s, ns); S = ns["S"]
en = json.load(open(f"{WK}/narr_en.json", encoding="utf-8")); em = json.load(open(f"{WK}/emph.json", encoding="utf-8"))
# 번호가 밀리므로 글로 다시
ns1 = {}; exec(open(f"{WK}/_seg/_merged_script.py", encoding="utf-8").read(), ns1)
old_t = [x[1] for x in ns1["S"] if x[0] == "N"]; t2e = {t: en.get(str(i + 1), "") for i, t in enumerate(old_t)}; t2m = {t: em["n"].get(str(i + 1)) for i, t in enumerate(old_t)}
t2e.update(EN); t2m.update(EMPH)
NT = [x[1] for x in S if x[0] == "N"]
json.dump({str(i + 1): t2e.get(t, "") for i, t in enumerate(NT)}, open(f"{WK}/narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
em["n"] = {str(i + 1): t2m[t] for i, t in enumerate(NT) if t2m.get(t)}
json.dump(em, open(f"{WK}/emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", len(NT), "· 영어 없음", [t for t in NT if not t2e.get(t)])
