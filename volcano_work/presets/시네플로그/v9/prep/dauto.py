# -*- coding: utf-8 -*-
"""대본에 대사(D)를 자동으로 더 넣는다 — dcand ✓ · 한국어 공식 자막(srt.txt)이 겹치는 줄 · 욕·감탄사만인 줄 빼고 · 이미 쓴 대사와 원본 3초 넘게.
① 기존 D 끼리 원본 3초 안이면 뒤 줄을 뺀다(묶어서 ✓ 면 묶음). ② 목표 초만큼 새 D 를 시간 순서 자리에 끼운다. 사용: python dauto.py 더할초"""
import ast, json, re, sys
ADD = float(sys.argv[1]) if len(sys.argv) > 1 else 300
OUT = "--out" in sys.argv
src = open("script.py", encoding="utf-8").read(); lines = src.splitlines(keepends=True)
T = ast.parse(src); SE = [n.value for n in T.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
ns = {}; exec(src, ns); S = ns["S"]
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
C = {}
for l in open("dcand.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("|", 4)
    if len(p) < 5 or p[3] != "✓": continue
    ids = tuple(json.loads(p[0])) if p[0].startswith("[") else (int(p[0]),)
    C[ids] = (float(p[2]), p[4])
SR = []
for r in open("srt.txt", encoding="utf-8"):
    p = r.rstrip("\n").split("\t")
    if len(p) >= 4: SR.append((float(p[1]), float(p[2]), re.sub(r"<[^>]+>", "", p[3]).strip()))
def span(ids): return min(L[i]["ws"] for i in ids), max(L[i]["we"] for i in ids)
# ① 기존 D 간격
zone = None; Dk = []
for k, x in enumerate(S):
    if x[0] == "ZONE": zone = x[1]; continue
    if x[0] == "D": Dk.append((k, zone, tuple(x[1]), span(x[1])))
drop = set()
for (k1, z1, i1, s1), (k2, z2, i2, s2) in zip(Dk, Dk[1:]):
    if k1 in drop: continue
    if z1 == z2 and abs(s2[0] - s1[1]) < 3.0 and abs(s1[0] - s2[1]) >= 0 and min(abs(s2[0] - s1[1]), abs(s1[0] - s2[1])) < 3.0:
        drop.add(k2)
used = [s for k, z, i, s in Dk if k not in drop]
# ② 후보
BAD = re.compile(r"젠장|씨발|빌어|망할|개새|병신|역겨|게이 자식|fuck|shit|damn|bitch", re.I)
INTJ = re.compile(r"^(oh|ah|uh|um|mhm|okay|ok|yeah|yes|no|hey|hi|wow|what|huh|ow|great|right)[.!?,]*$", re.I)
cand = []
for ids, (du, en) in C.items():
    if not (1.0 <= du <= 2.95): continue
    a, b = span(ids)
    ko = []
    for sa, sb, t in SR:
        if sa < b - 0.1 and sb > a + 0.1 and t not in ko: ko.append(t)
    if not ko or len(ko) > 2: continue
    kt = " / ".join(ko).replace("- ", "")
    if "♪" in kt or BAD.search(kt) or BAD.search(en): continue
    if all(INTJ.match(w.strip()) for w in en.split("/")): continue
    if len(re.sub(r"\s", "", kt)) > 30 or len(re.sub(r"[^가-힣]", "", kt)) < 4: continue
    cand.append((a, b, ids, kt, du))
# N 구간(이 장면 그림 구간) 안의 후보만 — 이야기 순서 자리 찾기
zone = None; Nr = []
for k, x in enumerate(S):
    if x[0] == "ZONE": zone = x[1]; continue
    if x[0] == "N" and zone == "main":
        rr = x[2] if isinstance(x[2], (list, tuple)) else [(x[2], x[3])]
        for a, b in rr: Nr.append((a, b, k))
cand.sort(key=lambda c: -(len(c[3]) + 8 * min(c[4], 2.5)))
pick = []; tot = 0
for a, b, ids, kt, du in cand:
    if tot >= ADD: break
    if any(a < ub + 3.0 and b > ua - 3.0 for ua, ub in used): continue
    host = [k for na, nb, k in Nr if na - 6 <= a and b <= nb + 6]
    if not host and OUT:   # 나레 구간 밖: 시간상 바로 앞 나레(구간 시작이 가장 늦은 것) 뒤 — 이야기 순서
        prev = [(na, k) for na, nb, k in Nr if na <= a]
        nxt = [na for na, nb, k in Nr if na > a]
        if prev and (not nxt or b < min(nxt) - 3): host = [max(prev)[1]]
    if not host: continue
    used.append((a, b)); pick.append((a, ids, kt, max(host))); tot += du
print("뺀 D", len(drop), "· 새 D", len(pick), f"· {tot:.0f}초")
# 쓰기: 새 D 는 host N 다음, 같은 host 안에서는 시간 순 (host 뒤 기존 D 들과도 시간 순)
ins = {}
for a, ids, kt, host in sorted(pick):
    ins.setdefault(host, []).append((a, f'("D", {list(ids)}, {json.dumps(kt, ensure_ascii=False)}),   # 자동(dauto)'))
out = []
for k, e in enumerate(SE):
    i = e.lineno - 1
    seg = "".join(lines[e.lineno - 1:e.end_lineno])
    if k in drop: lines[i] = "# (뺌·원본 3초 간격) " + lines[i]
for k in sorted(ins, reverse=True):
    # host N 뒤에 이어지는 D 묶음 끝 자리 찾기(다음 N/ZONE 전)
    j = k + 1
    while j < len(SE) and S[j][0] in ("D", "A"): j += 1
    block = list(range(k + 1, j))
    # 블록 안 기존 D 와 새 D 를 시간 순으로 섞기
    items = []
    for kk in block:
        x = S[kk]; t = span(x[1])[0] if x[0] == "D" else x[1]
        items.append((t, "".join(lines[SE[kk].lineno - 1:SE[kk].end_lineno])))
    ind = "".join(lines[SE[k].lineno - 1:SE[k].lineno])
    ind = ind[:len(ind) - len(ind.lstrip())]
    for t, s in ins[k]: items.append((t, ind + s + "\n"))
    items.sort(key=lambda z: z[0])
    first = SE[k].end_lineno  # host N 다음 줄 번호(0-기준 시작)
    last = SE[j - 1].end_lineno if block else SE[k].end_lineno
    lines[first:last] = [s for t, s in items]
open("script.py", "w", encoding="utf-8").write("".join(lines))
