# -*- coding: utf-8 -*-
# flipsheet 로 찾은 글자 조각 줄(k)에 {"noflip": True} (14v2 10-17). 사용: python -X utf8 noflip.py k1 k2 ... (flipsheet 칸 위 「k」 번호 — cut 전에, 줄 번호가 바뀌는 다른 손질보다 먼저)
import ast, sys
K = set(map(int, sys.argv[1:]))
src = open("script.py", encoding="utf-8").read(); lines = src.splitlines(keepends=True)
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
n = 0
for k in sorted(K, reverse=True):
    e = SE[k]; assert e.lineno == e.end_lineno, k
    seg = ast.get_source_segment(src, e); i = e.lineno - 1
    if "noflip" in seg: continue
    last = e.elts[-1]
    if isinstance(last, ast.Dict):
        ds = ast.get_source_segment(src, last); new = seg.replace(ds, ds[:-1] + (", " if len(last.keys) else "") + '"noflip": True}', 1)
    else:
        new = seg[:-1] + ', {"noflip": True})'
    lines[i] = lines[i].replace(seg, new, 1); n += 1
open("script.py", "w", encoding="utf-8").write("".join(lines)); print("noflip", n, "/", len(K))
