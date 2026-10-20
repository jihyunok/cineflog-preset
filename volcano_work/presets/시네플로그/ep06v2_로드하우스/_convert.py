# -*- coding: utf-8 -*-
"""옛 06 대본(ep06.py: R 구간 + (나레, [자막번호…]))을 v9 꼴(script.py)로 옮긴다 — 10-17 06 다시.
나레 구간 = 앞 줄의 마지막 대사 끝(없으면 R 시작)부터 이 줄 첫 대사 시작까지(앞뒤 2초 여유, 최소 8초). 대사는 sr(번호)."""
import json, os
OLD = os.path.expanduser("~/volcano_work/presets/시네플로그/ep06_로드하우스/ep06.py")
ns = {}; exec(open(OLD, encoding="utf-8").read(), ns); S0, SHORT = ns["S"], ns.get("SHORT", {})
K = {}
for r in open("srt.txt", encoding="utf-8"):
    p = r.rstrip("\n").split("\t")
    if len(p) >= 4: K[int(p[0])] = (float(p[1]), float(p[2]), p[3])
def ko(n): return SHORT.get(n) or K[n][2].replace("- ", "")
out = []; R = None; prev_end = None; zone = "hook"; n_hook = 0
def q(s): return json.dumps(s, ensure_ascii=False)
for x in S0:
    if x[0] == "R": R = (x[1], x[2]); prev_end = None; continue
    narr, dl = x
    if narr.startswith("이제 이 작품을") and zone != "outro": out.append('("ZONE", "outro"),'); zone = "outro"
    items = dl or []
    first = None
    for it in items:
        if isinstance(it, tuple) and it[0] == "A": first = first or it[1]; break
        n = it[0] if isinstance(it, tuple) else it
        first = K[n][0]; break
    a0 = prev_end if prev_end is not None else R[0]
    if first is None: a, b = R
    else:
        a, b = max(R[0] - 2, a0 - 1), first + 0.5
        if b - a < 8: a = min(a, b - 8)
    out.append(f'("N", {q(narr)}, {a:.1f}, {b:.1f}),')
    for it in items:
        if isinstance(it, tuple) and it[0] == "A":
            out.append(f'("A", {it[1] - 1:.1f}, {it[1] + it[2] + 1:.1f}, {min(it[2], 2.6)}),'); prev_end = it[1] + it[2]; continue
        if isinstance(it, tuple): n, txt = it[0], it[1]
        else: n, txt = it, ko(it)
        out.append(f'("D", sr({n}), {q(txt)}),'); prev_end = K[n][1]
    if zone == "hook":
        n_hook += 1
        if n_hook == 3: out.append('("ZONE", "main"),'); zone = "main"
head = open("script_head.py", encoding="utf-8").read()
open("script.py", "w", encoding="utf-8").write(head + "\n".join(out) + "\n]\n")
print("줄", len(out))
