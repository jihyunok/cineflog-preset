# -*- coding: utf-8 -*-
"""dchk 가 잡은 D 줄을 자동으로 바꾼다 — dsub(14v2 10-17, dfix.py 는 보여 주기만): 그 줄 대사(ids) 안의 dcand ✓ 묶음 중 가장 긴 것(3.15초 안)으로 바꾸고,
자막은 그 묶음 시각에 겹치는 공식 한국어 자막(srt.txt)으로 — 길면 원래 우리 자막(묶음이 원래 말의 60% 넘게 덮을 때만). 못 고치면 줄을 뺀다(주석).
사용: python -X utf8 dsub.py (작업 폴더: script.py · lines.json · dcand.txt · srt.txt)"""
import ast, json, re
src = open("script.py", encoding="utf-8").read(); lines = src.splitlines(keepends=True)
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
ns = {}; exec(src, ns); S = ns["S"]
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
C = {}
for l in open("dcand.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("|", 4)
    if len(p) < 5: continue
    ids = tuple(json.loads(p[0])) if p[0].startswith("[") else (int(p[0]),)
    C[ids] = (p[3], p[4])
SR = []
for r in open("srt.txt", encoding="utf-8"):
    p = r.rstrip("\n").split("\t")
    if len(p) >= 4: SR.append((float(p[1]), float(p[2]), re.sub(r"<[^>]+>", "", p[3]).replace("- ", "").strip()))
INTJ = re.compile(r"^(oh|ah|uh|um|mhm|okay|ok|yeah|yes|no|hey|hi|wow|what|huh|ow|right)[.!?,]*$", re.I)
def span(ids):
    ws = [L[i]["ws"] for i in ids if L[i]["ws"] is not None]; we = [L[i]["we"] for i in ids if L[i]["we"] is not None]
    return (min(ws), max(we)) if ws and we else (None, None)
fix = drop = 0
for k, x in enumerate(S):
    if x[0] != "D": continue
    ids = list(x[1]); e = SE[k]; i = e.lineno - 1
    if ids:
        a, b = span(ids)
        st = C.get(tuple(ids), ("없음", ""))[0]
        if a is not None and b - a <= 3.15 and "✓" in st: continue
    best = None
    for g, (st, en) in C.items():
        if "✓" not in st or not set(g) <= set(ids): continue
        ga, gb = span(g)
        if ga is None or not (0.8 <= gb - ga <= 3.15): continue
        if all(INTJ.match(w.strip()) for w in en.split("/")): continue
        if best is None or gb - ga > best[1] - best[0]: best = (ga, gb, g)
    if best is None:
        lines[i] = "# (뺌·dsub 맞는 ✓ 대사 없음) " + lines[i]; drop += 1; continue
    ga, gb, g = best
    ko = []
    for sa, sb, t in SR:
        if sa < gb - 0.1 and sb > ga + 0.1 and t not in ko: ko.append(t)
    kt = " / ".join(ko)
    a, b = span(ids)
    if not ko or len(ko) > 2 or len(re.sub(r"\s", "", kt)) > 30:
        if a is not None and (gb - ga) >= 0.6 * (b - a): kt = x[2]
        else: lines[i] = "# (뺌·dsub 자막 안 맞음) " + lines[i]; drop += 1; continue
    seg_ids = ast.get_source_segment(src, e.elts[1]); seg_t = ast.get_source_segment(src, e.elts[2])
    new = lines[i].replace(seg_ids, json.dumps(list(g)), 1).replace(seg_t, json.dumps(kt, ensure_ascii=False), 1)
    lines[i] = new.rstrip("\n") + "   # dsub\n"; fix += 1
open("script.py", "w", encoding="utf-8").write("".join(lines))
print("dsub 고침", fix, "· 뺌", drop)
