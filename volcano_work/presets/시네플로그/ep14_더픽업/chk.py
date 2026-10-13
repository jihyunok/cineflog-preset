# items.json 검사: 제목 낱말·욕설·18자
import json, re
it = json.load(open("items.json", encoding="utf-8"))
bad = re.compile("픽업|젠장|빌어|엿|씹|좆|새끼|이년|그년|섹스|거시기|똥|항문|꼴려|개자식|망할|썩을")
out = []
for q in it:
    t = q.get("text") or q.get("ko") or ""
    if bad.search(t): out.append(("BAD", q.get("i", q.get("ni")), t))
    if q["type"] == "D" and len(q["ko"]) > 18: out.append(("LONG", q["i"], q["ko"]))
D = sorted([q for q in it if q["type"] == "D"], key=lambda q: q["s"])
gap = sum(1 for a, b in zip(D, D[1:]) if b["s"] < a["s"] + a["d"] + 3.0)
open("tmp/chk.txt", "w", encoding="utf-8").write("\n".join(map(str, out)) + f"\n문제 {len(out)} · 대사 간격 3초 미만 {gap}\n")
