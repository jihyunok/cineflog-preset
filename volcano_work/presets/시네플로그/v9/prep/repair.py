# -*- coding: utf-8 -*-
"""plan_v9 --dry 문제를 자동으로 줄인다(작업 폴더에서): ① 대사끼리 원본 3초 간격 → 뒤 대사(자동 것 먼저) 뺌
② 나레 자리 없음 → 그 나레 구간 안의 자동(dauto) 대사를 하나 뺌, 없으면 구간을 앞뒤 6초씩 넓힘(최대 2번). 사용: python repair.py 반복수"""
import ast, json, os, re, subprocess, sys
PLAN = os.path.expanduser("~/volcano_work/presets/시네플로그/v9/plan_v9.py")
IT = int(sys.argv[1]) if len(sys.argv) > 1 else 6
WMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 1
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
SRCLEN = json.load(open("ep.json", encoding="utf-8"))["srclen"]
wid = {}
def t2s(t):
    p = t.split(":"); return int(p[0]) * 60 + float(p[1]) if len(p) == 2 else int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])
for it in range(IT):
    r = subprocess.run([sys.executable, PLAN, "--dry"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    out = r.stdout + r.stderr
    head = out.splitlines()[:3]
    probs = [l for l in out.splitlines() if "✗" in l]
    print(f"[{it}]", head[0] if head else "", "· 문제", len(probs))
    if not probs: break
    src = open("script.py", encoding="utf-8").read(); lines = src.splitlines(keepends=True)
    SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
    ns = {}; exec(src, ns); S = ns["S"]
    def span(ids): return min(L[i]["ws"] for i in ids), max(L[i]["we"] for i in ids)
    Ds = [(k, span(x[1]), "dauto" in lines[SE[k].lineno - 1]) for k, x in enumerate(S) if x[0] == "D"]
    kill = set(); widen = set()
    for p in probs:
        m = re.search(r"대사끼리 원본 3초 간격 어김 ([\d:.]+)~([\d:.]+) / ([\d:.]+)", p)
        if m:
            c = t2s(m.group(3)); a = t2s(m.group(1))
            cs = [d for d in Ds if abs(d[1][0] - c) < 0.15] or [d for d in Ds if abs(d[1][0] - a) < 0.15]
            cs.sort(key=lambda d: (not d[2], -d[0]))
            if cs: kill.add(cs[0][0])
            continue
        m = re.search(r"줄(\d+) (?:A .*?안에|조각 .*?까만 화면)", p)
        if m and "addA" in lines[SE[int(m.group(1))].lineno - 1]:
            kill.add(int(m.group(1))); continue
        m = re.search(r"줄(\d+) [NA] .*?\[([\d:.]+)~([\d:.]+)\] 안에", p)
        if m:
            k = int(m.group(1)); a, b = t2s(m.group(2)), t2s(m.group(3))
            inside = [d for d in Ds if d[2] and d[1][0] >= a - 1 and d[1][1] <= b + 1 and d[0] not in kill]
            if inside:
                inside.sort(key=lambda d: abs((d[1][0] + d[1][1]) / 2 - (a + b) / 2)); kill.add(inside[0][0])
            elif wid.get(k, 0) < WMAX: widen.add(k)
    for k in sorted(kill): lines[SE[k].lineno - 1] = ""
    for k in widen:
        e = SE[k]; j = 1 if e.elts[0].value == "A" else 2   # ("A", a, b, 길이) · ("N", 글, a, b)
        if not (isinstance(e.elts[j], ast.Constant) and isinstance(e.elts[j + 1], ast.Constant)): continue
        a, b = e.elts[j].value, e.elts[j + 1].value
        i = e.lineno - 1; seg = ast.get_source_segment(src, e)
        new = seg.replace(f"{ast.get_source_segment(src, e.elts[j])}, {ast.get_source_segment(src, e.elts[j + 1])}", f"{max(0, a - 6):.1f}, {min(SRCLEN, b + 6):.1f}", 1)
        lines[i] = lines[i].replace(seg, new); wid[k] = wid.get(k, 0) + 1
    open("script.py", "w", encoding="utf-8").write("".join(lines))
    print(f"    뺀 대사 {len(kill)} · 넓힌 나레 {len(widen)}")
open("_repair_last.log", "w", encoding="utf-8").write(out)
