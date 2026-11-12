# -*- coding: utf-8 -*-
"""판정자 a/b/c csv + 판정 틀 → 줄별_화면판정_최종.csv · 본체 시트 대조. 사용: python judge_merge.py <폴더> [본체.csv] [override.csv]
override.csv(idx,verdict,note) 는 본체가 크게 떠서 정한 줄 — 최종에 덮고 본체메모 칸에 남긴다."""
import csv, sys, os
D = sys.argv[1]; MY = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None; OV = sys.argv[3] if len(sys.argv) > 3 else None
rows = list(csv.DictReader(open(os.path.join(D, "줄별_화면판정.csv"), encoding="utf-8-sig")))
J = {}
for x in "abc":
    p = os.path.join(D, f"판정2_{x}.csv")
    if not os.path.exists(p): continue
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        try: J[int(r["idx"])] = (r["verdict"].strip().upper(), r["note"].strip(), x)
        except Exception: pass
ov = {}
if OV and os.path.exists(OV):
    for r in csv.DictReader(open(OV, encoding="utf-8-sig")): ov[int(r["idx"])] = (r["verdict"].strip().upper(), r["note"].strip())
miss = []
for r in rows:
    i = int(r["idx"]); v = J.get(i)
    if not v: miss.append(i); r["verdict"] = ""; r["note"] = ""; r["who"] = ""; continue
    r["verdict"], r["note"], r["who"] = v
    if i in ov: r["본체"] = f"{ov[i][0]} — {ov[i][1]}"; r["verdict"] = ov[i][0]
out = os.path.join(D, "줄별_화면판정_최종.csv")
keys = list(rows[0].keys()) + [k for k in ("who", "본체") if k not in rows[0]]
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); [w.writerow({k: r.get(k, "") for k in keys}) for r in rows]
n = len(rows); c = {v: sum(1 for r in rows if r["verdict"] == v) for v in "OPX"}
tot = sum(float(r["dur"]) for r in rows); to = sum(float(r["dur"]) for r in rows if r["verdict"] == "O")
print(f"줄 {n} · O {c['O']} {100*c['O']/n:.1f}% · P {c['P']} · X {c['X']} · 빈칸 {len(miss)} {miss[:20]} · 시간 O {to:.1f}/{tot:.1f}초 {100*to/tot:.1f}%")
if MY:
    my = {int(r["idx"]): r["verdict"].strip().upper() for r in csv.DictReader(open(MY, encoding="utf-8-sig"))}
    same = [i for i in my if J.get(i, ("",))[0] == my[i]]; diff = [(i, my[i], J.get(i, ("?",))[0], J.get(i, ("", "", ""))[1][:80]) for i in my if J.get(i, ("",))[0] != my[i]]
    print(f"본체 대조 {len(same)}/{len(my)} 같음"); [print("  다름", d) for d in diff]
