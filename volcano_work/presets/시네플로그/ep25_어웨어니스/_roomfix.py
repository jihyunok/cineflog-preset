# -*- coding: utf-8 -*-
# plan --dry 의 「나레 자리 없음」 줄 구간 안 대사(D)를 빼고, 「0.5초 깜빡」 조각의 대사 줄도 뺀다 (25편 10-27)
import ast, json, re
log = open("_plan_dry.log", encoding="utf-8").read()
src = open("script.py", encoding="utf-8").read(); L = src.split("\n")
E = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign)][0].elts
ns = {}; exec(src, ns); S = ns["S"]
LN = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
drop = set()
for k in map(int, re.findall(r"✗ 줄(\d+) N .*?놓을 자리 없음", log)):
    x = S[k]; spans = x[2] if isinstance(x[2], list) else [(x[2], x[3])]
    for j, y in enumerate(S):
        if y[0] == "D" and any(a - 1 < LN[y[1][0]]["s"] < b + 1 for a, b in spans): drop.add(j)
W = json.load(open("windows_dry.json", encoding="utf-8"))
for t in map(float, re.findall(r"깜빡 조각 (\d+):([\d.]+)", log) and [int(m) * 60 + float(s) for m, s in re.findall(r"깜빡 조각 (\d+):([\d.]+)", log)]):
    for w in W:
        if abs(w["a"] - t) < 0.06 and w["kind"] == "D": drop.add(w["k"])
for k in sorted(drop):
    ln = E[k].lineno - 1; print(k, L[ln][:50]); L[ln] = "# (뺌·나레 자리/깜빡 10-27) " + L[ln]
open("script.py", "w", encoding="utf-8").write("\n".join(L)); print("뺌", len(drop))
