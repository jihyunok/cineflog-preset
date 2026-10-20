# -*- coding: utf-8 -*-
# 나레 구간이 [(a, b)] 한 개짜리 목록이면 a, b 로 푼다 — 목록은 구간마다 조각 1개라 길게 못 깐다 (14v2 10-17)
import ast, json
src = open("script.py", encoding="utf-8").read(); lines = src.splitlines(keepends=True)
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
n = 0
for e in SE:
    if not (isinstance(e, ast.Tuple) and isinstance(e.elts[0], ast.Constant) and e.elts[0].value == "N"): continue
    r = e.elts[2]
    if isinstance(r, ast.List) and len(r.elts) == 1:
        a, b = [el.value for el in r.elts[0].elts]
        i = e.lineno - 1; seg = ast.get_source_segment(src, r)
        lines[i] = lines[i].replace(seg, f"{float(a)}, {float(b)}", 1); n += 1
open("script.py", "w", encoding="utf-8").write("".join(lines))
print("풀었음", n)
