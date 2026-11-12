# -*- coding: utf-8 -*-
"""옛 판 줄별 판정(최종 csv) → 토막마다 KNOWN 글 → BRIEF_X.md (11-12 31v2)."""
import csv, json, re
WK = r"D:\cine_work\ep31v2_잭리처"; SEG = WK + r"\_seg"
rows = list(csv.DictReader(open(r"D:\cine_work\재검사_1107\ep31_전\줄별_화면판정_최종.csv", encoding="utf-8-sig")))
ns = {}; exec(open(WK + r"\_v1_script.py", encoding="utf-8").read(), ns); S = ns["S"]
nk = [k for k, x in enumerate(S) if x[0] == "N"]   # n(1부터) → k
def norm(t): return re.sub(r"[\s.,?!·…'\"]", "", t)
bad = 0
for r in rows:
    k = nk[int(r["blk"]) - 1]; r["k"] = k
    if norm(r["text"]) not in norm(S[k][1]): bad += 1
print("블록→k 글 안 맞음", bad)
spans = [(0, 91), (91, 228), (228, 363), (363, 494)]
brief = open(SEG + r"\BRIEF.md", encoding="utf-8").read()
for X, (k0, k1) in zip("1234", spans):
    rs = [r for r in rows if k0 <= r["k"] < k1]
    c = {v: sum(1 for r in rs if r["verdict"] == v) for v in "OPX"}
    out = [f"옛 판 이 토막 나레 자막 {len(rs)}줄: O {c['O']} · P {c['P']} · X {c['X']} (O {100*c['O']/max(1,len(rs)):.0f}%). 아래는 P·X 줄(옛 글·옛 구간 기준):"]
    for r in rs:
        if r["verdict"] in ("P", "X"):
            out.append(f"- k{r['k']} 「{r['text']}」 {r['verdict']} — {r['note'][:150]}")
    open(SEG + rf"\BRIEF_{X}.md", "w", encoding="utf-8").write(brief.replace("{X}", X).replace("{KNOWN}", "\n".join(out)))
    print(X, len(rs), c)
