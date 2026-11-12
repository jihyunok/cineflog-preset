# -*- coding: utf-8 -*-
"""토막 sega·b·c.py 를 기준 대본(_seg3/_base_script.py = v2 대본 + 본체 5블록)에 끼워 새 script.py · narr_en.json · emph.json 을 만든다(11-12 33v3). 기준 대본은 그대로 남는다."""
import ast, json, os, sys
WK = r"D:\cine_work\ep33v3_콜래트럴"; SEG = os.path.join(WK, "_seg4")
src = open(os.path.join(SEG, "_base_script.py"), encoding="utf-8").read(); L = src.splitlines(keepends=True)
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
end_i = [i for i, l in enumerate(L) if l.strip() == "]"][-1]
segs = []
for X in "ab":
    g = {}; exec(open(os.path.join(SEG, f"seg{X}.py"), encoding="utf-8").read(), g); segs.append(g)
segs.sort(key=lambda g: g["SPAN"][0])
out = []; pos = 0
for g in segs:
    k0, k1 = g["SPAN"]; a = SE[k0].lineno - 1; b = SE[k1].lineno - 1 if k1 < len(SE) else end_i
    out.append("".join(L[pos:a])); out.append(g["LINES"].strip("\n") + "\n"); pos = b
out.append("".join(L[pos:]))
new = "".join(out)
ns = {}; exec(new, ns); S = ns["S"]
open(os.path.join(WK, "script.py"), "w", encoding="utf-8").write(new)
ns1 = {}; exec(src, ns1); oe = json.load(open(os.path.join(SEG, "_base_narr_en.json"), encoding="utf-8")); om = json.load(open(os.path.join(SEG, "_base_emph.json"), encoding="utf-8"))
t2e, t2m = {}, {}; n = 0
for x in ns1["S"]:
    if x[0] == "N":
        n += 1; t2e[x[1]] = oe.get(str(n), "")
        if str(n) in om["n"]: t2m[x[1]] = om["n"][str(n)]
for g in segs: t2e.update(g.get("EN", {})); t2m.update(g.get("EMPH", {}))
en, em, miss = {}, {}, []; n = 0
for x in S:
    if x[0] == "N":
        n += 1; en[str(n)] = t2e.get(x[1], "")
        if not en[str(n)]: miss.append((n, x[1]))
        if x[1] in t2m and t2m[x[1]][0] in x[1]: em[str(n)] = t2m[x[1]]
json.dump(en, open(os.path.join(WK, "narr_en.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
om["n"] = em; om["why"] = om.get("why", "") + " · 11-12 33v3 4차: 글로 새 번호에 옮김"
json.dump(om, open(os.path.join(WK, "emph.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("줄", len(S), "· 나레", n, "· 영어 없음", miss, "· 강조", len(em))
for g in segs:
    for c in g.get("CHANGES", []): print("  -", c)
