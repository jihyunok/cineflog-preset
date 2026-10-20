# -*- coding: utf-8 -*-
"""나레 그림 구간 바꾸기·줄 빼기 (14v2 10-17). 사용: python -X utf8 nset.py 고칠표.py (작업 폴더에서)
고칠표: R = {"나레 앞글자": [(a,b),...] 또는 None(나레 뺌)} · T = {"나레 앞글자": "새 글"}(R 에도 있어야 함) · DD = [대사 ids 리스트, ...](뺄 대사)"""
import ast, json, sys, shutil
fx = {}; exec(open(sys.argv[1], encoding="utf-8").read(), fx)
R, DD, T = fx.get("R", {}), [list(x) for x in fx.get("DD", [])], fx.get("T", {})
src = open("script.py", encoding="utf-8").read(); lines = src.splitlines(keepends=True)
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
ns = {}; exec(src, ns); S = ns["S"]
hit = set(); dh = 0
for k, (e, x) in enumerate(zip(SE, S)):
    i = e.lineno - 1
    if x[0] == "N":
        for p, rr in R.items():
            if not x[1].startswith(p): continue
            hit.add(p)
            if rr is None: lines[i] = "# (뺌·_nset) " + lines[i]; continue
            opt = [ast.get_source_segment(src, el) for el in e.elts[2:] if isinstance(el, ast.Dict)]
            new = f'("N", {json.dumps(T.get(p, x[1]), ensure_ascii=False)}, {(f"{float(rr[0][0])}, {float(rr[0][1])}" if len(rr) == 1 else [(float(a), float(b)) for a, b in rr])}' + (", " + opt[0] if opt else "") + ")"
            assert e.lineno == e.end_lineno, (k, "여러 줄 나레")
            lines[i] = lines[i].replace(ast.get_source_segment(src, e), new, 1)
    elif x[0] == "D" and list(x[1]) in DD:
        lines[i] = "# (뺌·_nset) " + lines[i]; dh += 1
open("script.py", "w", encoding="utf-8").write("".join(lines))
print("나레", len(hit), "· 못 찾음", [p for p in R if p not in hit], "· 뺀 대사", dh, "/", len(DD))
