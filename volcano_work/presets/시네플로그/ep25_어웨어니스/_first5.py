# -*- coding: utf-8 -*-
# 앞 5분(화면) 안에서 나레 없이 대사가 5줄 넘게 이어지면 자동(dauto) 줄부터 빼서 4줄 이하로 (관문 ⑮) — 25편 10-27
import ast, json
src = open("script.py", encoding="utf-8").read(); L = src.split("\n")
E = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign)][0].elts
ns = {}; exec(src, ns); S = ns["S"]
W = json.load(open("windows_dry.json", encoding="utf-8"))
first = {}
for w in W: first.setdefault(w["k"], w["a"])
ks = sorted(k for k, a in first.items() if a < 300)
runs, cur = [], []
for k in ks:
    t = S[k][0]
    if t == "D": cur.append(k)
    elif t == "N":
        if cur: runs.append(cur); cur = []
if cur: runs.append(cur)
drop = set()
for r in runs:
    while len(r) > 4:
        auto = [k for k in r if "자동(dauto)" in L[E[k].lineno - 1] and not (len(S[k]) > 3 and S[k][3].get("event"))]
        pool = auto or [k for k in r[1:-1] if not (len(S[k]) > 3 and S[k][3].get("event"))]
        k = pool[len(pool) // 2]; drop.add(k); r.remove(k)
for k in sorted(drop):
    ln = E[k].lineno - 1; L[ln] = "# (뺌·앞 5분 대사 5줄 넘음 10-27) " + L[ln]
open("script.py", "w", encoding="utf-8").write("\n".join(L)); print("뺌", len(drop))
