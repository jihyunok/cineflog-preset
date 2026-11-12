# -*- coding: utf-8 -*-
"""post.py 뒤(11-12 31v2) — flow_check ① 진짜 장소 바뀜 3곳에 짧은 나레를 대사 사이에 넣음(컷 설명·대사 시각 확인, 아래 주석).
그리고 같은 흐름인 4곳은 ep.json flow_ok 에 곳마다 이유(컷 설명 근거)."""
import json
WK = r"D:\cine_work\ep31v2_잭리처"
INS = [  # (이 대사 id 줄 바로 뒤, 넣을 N 줄, EN, EMPH 또는 None)
 (1148, '("N", "헬렌의 사무실엔 사건 사진이 가득하죠.", [(4092.0, 4097.3)], {"sent": True}),   # 11-12 본체: flow ① 찰리 차 → 헬렌 사무실 · 컷 설명 4091.3~4097.5 책상 위 증거 사진·사망 진단서',
  "Helen's office is covered in case photos.", None),
 (1442, '("N", "화면 속 남자는 바로 찰리였죠.", [(5651.5, 5655.0)], {"sent": True}),   # 11-12 본체: flow ① 사격장 → 헬렌 사무실 · 프레임 봄: 5649.2 감시 화면 속 모자 쓴 찰리, 5650.2 는 캐시 → 컷 설명 5651.5~5655.0 감시 화면 찰리 얼굴 클로즈업으로 (전화 울리는 컷 5655 는 다음 대사 창과 3초 간격 안이라 못 씀 — 통화 교차는 flow_ok)',
  "The man on the screen is Charlie.", ("바로 찰리", "reveal")),
 (1603, '("N", "그 시각 더 젝은 헬렌을 마주하고 있죠.", [(6313.9, 6319.6)], {"sent": True}),   # 11-12 본체: flow ① 채석장 → 더 젝 은신처 · 컷 설명 6310.4 더 젝을 보는 헬렌·6314.8 헬렌을 노려보는 더 젝',
  "Meanwhile, the Zec faces Helen.", None),
]

# 제브 이유 0.76 「쓰러진 헬렌」 — 프레임 봄(s_helen.jpg): 5933.3 전기 충격기 불꽃·5937.6~5941.0 엘리베이터 바닥에 쓰러진 헬렌·5943.6 에머슨·찰리·대머리 부하·5951.1 헬렌을 들고 나가는 남자들
OLD = '("N", "헬렌을 곁눈질하는 에머슨, 그가 바로 더 젝의 한패였죠. 쓰러진 헬렌은 찰리 일당에게 끌려갑니다.", [[(5925.2, 5928.3), (5928.4, 5932.4)], [(5938.5, 5941.5), (5943.5, 5948.7), (5951.0, 5956.6)]], {"sent": True})'
NEW = '("N", "헬렌을 곁눈질하는 에머슨, 그가 바로 더 젝의 한패였죠. 전기 충격기에 쓰러진 헬렌. 찰리 일당이 그녀를 들고 나갑니다.", [[(5925.2, 5928.3), (5928.4, 5932.4)], (5937.4, 5941.4), [(5943.5, 5948.5), (5951.0, 5954.0)]], {"sent": True})'
NEW_EN = "Emerson glances at Helen; he is the Zec's man. Helen collapses from a taser. Charlie's crew carries her out."
s = open(f"{WK}/script.py", encoding="utf-8").read()
assert s.count(OLD) == 1; _ot = eval(OLD)[1]; _nt = eval(NEW)[1]; s = s.replace(OLD, NEW)
en = json.load(open(f"{WK}/narr_en.json", encoding="utf-8")); em = json.load(open(f"{WK}/emph.json", encoding="utf-8"))
ns0 = {}; exec(s, ns0); T0 = [x[1] for x in ns0["S"] if x[0] == "N"]
t2e = {t: en.get(str(i + 1), "") for i, t in enumerate(T0)}; t2m = {t: em["n"].get(str(i + 1)) for i, t in enumerate(T0)}
t2e[_nt] = NEW_EN; t2m[_nt] = t2m.get(_nt)
L = s.splitlines(keepends=True)
for did, line, e, m in INS:
    t = eval(line.split("   #")[0].rstrip().rstrip(","))[1]
    if t in t2e: print("이미 있음", t); continue
    idx = [i for i, l in enumerate(L) if l.lstrip().startswith(f'("D", [{did}]') or l.lstrip().startswith(f'("D", [{did},')]
    assert len(idx) == 1, (did, idx)
    L.insert(idx[0] + 1, line + "\n"); t2e[t] = e; t2m[t] = list(m) if m else None
s = "".join(L); open(f"{WK}/script.py", "w", encoding="utf-8").write(s)
ns = {}; exec(s, ns); S = ns["S"]; NT = [x[1] for x in S if x[0] == "N"]
json.dump({str(i + 1): t2e.get(t, "") for i, t in enumerate(NT)}, open(f"{WK}/narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
em["n"] = {str(i + 1): t2m[t] for i, t in enumerate(NT) if t2m.get(t) and t2m[t][0] in t}
json.dump(em, open(f"{WK}/emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", len(NT), "· 영어 없음", [t[:20] for t in NT if not t2e.get(t)], "· 강조", len(em["n"]))
