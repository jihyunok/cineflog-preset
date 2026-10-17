# -*- coding: utf-8 -*-
"""지금 대본(script.py)에 넣을 수 있는 대사 후보 — dcand ✓ 이면서 이미 쓴 대사 창과 원본 3초 넘게 떨어진 줄(1~2줄 묶음, 1초 이상).
사용: python dfree.py 시작초 끝초"""
import json, sys
a0, a1 = float(sys.argv[1]), float(sys.argv[2])
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
C = {}
for l in open("dcand.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("|", 4)
    if len(p) < 5 or p[3] != "✓": continue
    ids = tuple(json.loads(p[0])) if p[0].startswith("[") else (int(p[0]),)
    m, s = p[1].split(":"); C[ids] = (int(m) * 60 + float(s), float(p[2]), p[4])
used = []
for x in ns["S"]:
    if x[0] == "D":
        ids = tuple(x[1]) if isinstance(x[1], list) else (x[1],)
        if ids in C: used.append((C[ids][0], C[ids][0] + C[ids][1]))
for ids, (t, d, en) in sorted(C.items(), key=lambda kv: kv[1][0]):
    if not (a0 <= t <= a1) or len(ids) > 2 or d < 1.0: continue
    if all(t + d + 3.0 <= u0 or t >= u1 + 3.0 for u0, u1 in used): print(f"{t:7.1f} {str(list(ids)):>12} {d:.1f}s {en[:100]}")
