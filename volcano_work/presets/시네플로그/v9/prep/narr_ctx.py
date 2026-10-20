# -*- coding: utf-8 -*-
"""나레 다시 쓰기용 맥락표 — 완성된 편의 script.py 에서 S 구간을 골라, 나레 줄마다 (옛 글·그림 구간·글자 수 한도·그 구간 그림 설명)와
앞뒤 대사(우리 자막)·소리 장면을 화면 순서대로 적는다. 10-20 03 v2(출발 비디오여행식 나레로 전체 다시 쓰기)에서 서브에이전트에게 준 재료.
글자 수 한도 = 옛 글자 수(띄어쓰기 뺌) × 1.12 + 1 — 그림 구간과 3초 간격이 옛 나레 길이에 맞춰 짜여 있어서 길게 쓰면 plan 이 못 놓는다.
사용: python narr_ctx.py 작업폴더 S시작 S끝 출력.md   (작업폴더 = script.py·lines.json·shots.json 이 있는 롱폼 폴더)"""
import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
WD, A, B, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
here = os.getcwd(); os.chdir(WD)
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
SH = json.load(open("shots.json", encoding="utf-8"))
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
os.chdir(here)
def shots(a, b):
    out = []
    for x in SH:
        if x["s"] < b and x["e"] > a and x["e"] - x["s"] > 0.5:
            d = re.sub(r"^(In|At|Inside) [^,]*, ", "", x["desc"]).replace("Novalee Nation", "Novalee")
            if not out or out[-1][1] != d: out.append((x["s"], d))
    return "; ".join(f"{s:.0f}s {d}" for s, d in out[:8])
ni = sum(1 for x in S[:A] if x[0] == "N")
rows = []
for k in range(A, B + 1):
    x = S[k]
    if x[0] == "ZONE": rows.append(f"\n### 구역 {x[1]}\n"); continue
    if x[0] == "N":
        ni += 1; n0 = len(re.sub(r"\s", "", x[1]))
        rng = [(x[2], x[3])] if not isinstance(x[2], list) else [tuple(r) for r in x[2]]
        rows.append(f"- **N S{k} (n{ni:03d})** 옛: {x[1]}\n  - 그림 {', '.join(f'{a:.1f}~{b:.1f}' for a, b in rng)} · 옛 {n0}자 → **새 글 {int(n0 * 1.12) + 1}자 이하(띄어쓰기 뺌)**\n  - 그 구간 그림: {shots(rng[0][0], rng[-1][1])}")
    elif x[0] == "D":
        ids = x[1] if isinstance(x[1], list) else [x[1]]
        rows.append(f"- D S{k} 대사 「{x[2]}」 ({' '.join(L[i]['en'] for i in ids)})")
    elif x[0] == "A":
        rows.append(f"- A S{k} 원본 소리 장면 {x[1]:.0f}~{x[2]:.0f}s — {shots(x[1], x[2])[:120]}")
open(OUT, "w", encoding="utf-8").write("\n".join(rows) + "\n")
print(OUT, "나레", sum(1 for r in rows if r.startswith("- **N")), "줄")
