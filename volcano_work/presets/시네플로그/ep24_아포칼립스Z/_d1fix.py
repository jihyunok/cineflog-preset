# -*- coding: utf-8 -*-
# D 줄이 3초 넘거나 ✗ 면 그 묶음 안 ✓·3초 이하 한 id(가장 긴 것)로 줄인다
import json, re
C = {}
for l in open("dcand.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("|", 4)
    if len(p) < 5: continue
    ids = tuple(json.loads(p[0])) if p[0].startswith("[") else (int(p[0]),)
    C[ids] = (float(p[2]), p[3])
src = open("script.py", encoding="utf-8").read().split("\n"); n = 0
for i, l in enumerate(src):
    m = re.match(r'\("D", \[([\d, ]+)\]', l)
    if not m: continue
    ids = tuple(int(x) for x in m.group(1).split(","))
    c = C.get(ids)
    if c and c[1] == "✓" and c[0] <= 3.0: continue
    best = None
    for k in ids:
        v = C.get((k,))
        if v and v[1] == "✓" and v[0] <= 3.0 and (best is None or v[0] > best[1]): best = (k, v[0])
    if best:
        src[i] = l.replace(f"[{m.group(1)}]", f"[{best[0]}]", 1); n += 1
    else: print("못 고침", i + 1, l[:60])
open("script.py", "w", encoding="utf-8").write("\n".join(src)); print("고침", n)
