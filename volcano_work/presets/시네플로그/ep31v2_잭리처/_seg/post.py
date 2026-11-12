# -*- coding: utf-8 -*-
"""merge.py 뒤 본체 손질(11-12 31v2) — 통독에서 고친 줄. 글로 narr_en·emph 다시 붙임(merge 를 다시 돌리면 이것도 다시)."""
import json
WK = r"D:\cine_work\ep31v2_잭리처"
P = [  # (옛 글, 새 글, 새 EN 또는 None)
 ("흰 승합차 한 대가 피츠버그로 들어섭니다. 남자는 총알을 손수 만들었죠. 장갑 낀 손으로 운전대를 쥔 남자.",
  "흰 승합차 한 대가 피츠버그로 들어섭니다. 남자는 총알을 손수 만들었죠. 장갑 낀 손이 운전대를 쥐고 있죠.", None),   # 앞 줄 「이름뿐.」과 명사 끝 연달아
 ("아버지는 딸의 기사를 내밉니다. 그리고 헬렌에게 실력 있는 변호사냐고 묻는데요.",
  "피해자 아버지는 딸의 기사를 내밉니다. 그리고 헬렌에게 실력 있는 변호사냐고 묻는데요.", None),   # 장면 바뀌는 첫 줄 — 누구의 아버지인지(프레임 봄: 1537.3 신문·권총 위로 내미는 손, 1542.8 회색 머리 피해자 아버지. 로딘 아님)
]
P += [
 ("그 차의 주인은 리벤더 기업. 올라인 아처와 소송을 벌이던 회사였죠. 리처는 다섯 명을 무작위로 쐈다는 게 말이 되냐고 묻죠.",
  "그 차의 주인은 리벤더 기업. 올라인 아처와 얽힌 회사였죠. 리처는 다섯 명을 무작위로 쐈다는 게 말이 되냐고 묻죠.",
  "The car belongs to Lebendauer Enterprises. A company tied to Oline Archer. Reacher asks if killing five people at random makes any sense."),   # 제브 사실 0.68 — 서류는 소송이 아니라 합의서(컷 설명 4154.1 settlement agreement between Oline Archer and Lebendauer)
 ("지검장 아버지에게 비리를 털어놓는 헬렌.", "리벤더의 비리를 아버지에게 털어놓는 헬렌.", "Helen tells her father about Lebendauer's corruption."),   # 제브 모름 0.88 — 무슨 비리인지
 ("리처는 바의 실력으로는 그 자리에서 그렇게 쏠 수 없었다고 말합니다.", "리처는 훈련받은 바라면 증거를 남기지 않았을 거라고 말합니다.",
  "Reacher says a trained sniper like Barr would never have left that evidence."),   # 제브 사실 0.60 — 대사 3760 「99% 불리한 증거들은 이라크 때와 딴판」·3764 「숙련된 저격수」
]

s = open(f"{WK}/script.py", encoding="utf-8").read()
en = json.load(open(f"{WK}/narr_en.json", encoding="utf-8")); em = json.load(open(f"{WK}/emph.json", encoding="utf-8"))
ns0 = {}; exec(s, ns0); T0 = [x[1] for x in ns0["S"] if x[0] == "N"]
t2e = {t: en.get(str(i + 1), "") for i, t in enumerate(T0)}; t2m = {t: em["n"].get(str(i + 1)) for i, t in enumerate(T0)}
for a, b, e in P:
    if s.count(f'"{a}"') != 1: print("못 찾음(이미 고침?)", a[:30]); continue
    s = s.replace(f'"{a}"', f'"{b}"'); t2e[b] = e or t2e.get(a, ""); t2m[b] = t2m.get(a)
open(f"{WK}/script.py", "w", encoding="utf-8").write(s)
ns = {}; exec(s, ns); NT = [x[1] for x in ns["S"] if x[0] == "N"]
json.dump({str(i + 1): t2e.get(t, "") for i, t in enumerate(NT)}, open(f"{WK}/narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
em["n"] = {str(i + 1): t2m[t] for i, t in enumerate(NT) if t2m.get(t) and t2m[t][0] in t}
json.dump(em, open(f"{WK}/emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", len(NT), "· 영어 없음", [t[:20] for t in NT if not t2e.get(t)], "· 강조", len(em["n"]))
