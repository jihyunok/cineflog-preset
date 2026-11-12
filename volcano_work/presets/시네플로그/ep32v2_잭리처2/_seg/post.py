# -*- coding: utf-8 -*-
"""merge.py 뒤 본체 손질(11-07 32v2) — 「~고요」 금지(텔레그램 「"~고요" 는 쓰지마」 · README 말투) 세 줄. 옛 대본에서 넘어온 「체포됐고요·차례라고요·필요해서였다고요」.
merge 를 다시 돌리면 이것도 다시. 33v2 post.py 와 같은 방식(글로 narr_en·emph 다시 붙임)."""
import json
WK = r"D:\cine_work\ep32v2_잭리처2"
P = [
 ("다음 날 터너가 체포됐고요.", "그리고 다음 날, 터너가 체포된 거죠."),
 ("사냥꾼이 될 차례라고요.", "사냥꾼이 될 차례라는 거죠."),
 ('("N", "돈이 필요해서였다고요."', '("N", "돈이 필요해서였다는 거죠."'),
]
OLD2NEW = {
 "다시 만난 변호사 무어크로프트 대령은, 터너가 아프간에 보낸 수사관 둘이 살해당했다고 털어놓습니다. 다음 날 터너가 체포됐고요.":
 "다시 만난 변호사 무어크로프트 대령은, 터너가 아프간에 보낸 수사관 둘이 살해당했다고 털어놓습니다. 그리고 다음 날, 터너가 체포된 거죠.",
 "리처는 터너에게 새 옷을 사 오며 말합니다. 이제 도망자가 아니라 사냥꾼이 될 차례라고요.":
 "리처는 터너에게 새 옷을 사 오며 말합니다. 이제 도망자가 아니라 사냥꾼이 될 차례라는 거죠.",
 "돈이 필요해서였다고요.": "돈이 필요해서였다는 거죠.",
}
s = open(f"{WK}/script.py", encoding="utf-8").read()
for a, b in P:
    assert s.count(a) == 1, a[:40]; s = s.replace(a, b)
open(f"{WK}/script.py", "w", encoding="utf-8").write(s)
ns = {}; exec(s, ns); S = ns["S"]
en = json.load(open(f"{WK}/narr_en.json", encoding="utf-8")); em = json.load(open(f"{WK}/emph.json", encoding="utf-8"))
ns1 = {}; exec(open(f"{WK}/_seg/_merged_script.py", encoding="utf-8").read(), ns1)
old_t = [x[1] for x in ns1["S"] if x[0] == "N"]
t2e = {OLD2NEW.get(t, t): en.get(str(i + 1), "") for i, t in enumerate(old_t)}
t2m = {OLD2NEW.get(t, t): em["n"].get(str(i + 1)) for i, t in enumerate(old_t)}
NT = [x[1] for x in S if x[0] == "N"]
json.dump({str(i + 1): t2e.get(t, "") for i, t in enumerate(NT)}, open(f"{WK}/narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
em["n"] = {str(i + 1): t2m[t] for i, t in enumerate(NT) if t2m.get(t) and t2m[t][0] in t}
json.dump(em, open(f"{WK}/emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", len(NT), "· 영어 없음", [t for t in NT if not t2e.get(t)], "· 강조", len(em["n"]))
