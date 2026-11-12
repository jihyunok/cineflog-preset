# -*- coding: utf-8 -*-
"""merge2.py 뒤(11-12 31v2 2차) — 실제 녹음 길이로 plan 「자리 없음」 손질. (merge2 를 다시 돌리면 이것도 다시)"""
import json
WK = r"D:\cine_work\ep31v2_잭리처"
R = [
 ("거스름돈 동전을 집어 든 리처. 그는 무언가를 떠올립니다. 주차기 동전 속 바의 지문이죠.",
  "거스름돈 동전을 집어 든 리처. 그는 무언가를 떠올립니다. 동전 속 바의 지문이죠.",
  "Reacher picks up his change. Something comes to mind. Barr's print on the coin."),   # 셋째 문장 녹음 2.16초 → 1866.3(소총 회상 컷) 앞까지 0.2초 모자람 — 줄임
]
s = open(f"{WK}/script.py", encoding="utf-8").read()
en = json.load(open(f"{WK}/narr_en.json", encoding="utf-8")); em = json.load(open(f"{WK}/emph.json", encoding="utf-8"))
ns0 = {}; exec(s, ns0); T0 = [x[1] for x in ns0["S"] if x[0] == "N"]
t2e = {t: en.get(str(i + 1), "") for i, t in enumerate(T0)}; t2m = {t: em["n"].get(str(i + 1)) for i, t in enumerate(T0)}
for a, b, e in R:
    assert s.count(f'"{a}"') == 1, a[:30]
    s = s.replace(f'"{a}"', f'"{b}"'); t2e[b] = e or t2e.get(a, ""); t2m[b] = t2m.get(a)
open(f"{WK}/script.py", "w", encoding="utf-8").write(s)
ns = {}; exec(s, ns); NT = [x[1] for x in ns["S"] if x[0] == "N"]
json.dump({str(i + 1): t2e.get(t, "") for i, t in enumerate(NT)}, open(f"{WK}/narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
em["n"] = {str(i + 1): t2m[t] for i, t in enumerate(NT) if t2m.get(t) and t2m[t][0] in t}
json.dump(em, open(f"{WK}/emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", len(NT), "· 영어 없음", [t[:20] for t in NT if not t2e.get(t)], "· 강조", len(em["n"]))
