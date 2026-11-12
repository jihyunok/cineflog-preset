# -*- coding: utf-8 -*-
"""관문 ⑨(나레↔그림) 걸린 줄의 그림 구간을 「그 문장이 말하는 컷」으로 좁힌다 (10-23 드루와 02 — 토막 대본 구간이 넓어 plan 이 엉뚱한 컷을 고름, dry 307/2037 조각).
걸린 줄마다 구간 안 컷(shots.json) 하나하나를 제브(나레그림_맞음.json)로 판정 → 맞는 컷(맞음 0.5+·어긋남 0.5 안) 이어진 덩어리만 새 구간으로.
새 구간이 나레 길이(글자 ÷ 6.5 × 2.2)보다 짧으면 맞는 컷 옆의 어긋나지 않는 컷으로 넓힌다. 맞는 컷이 하나도 없으면 손대지 않고 목록에만(np_narrow_manual.txt).
고치는 곳: 대본 원본 파일들(--files 토막 script_part.py · hook_outro.py)에서 그 나레 글 줄의 구간만 바꿈.
사용: python np_narrow.py --files part1/script_part.py … hook_outro.py   (작업 폴더: script.py · windows.json(또는 --win windows_dry.json) · jev_np_out.jsonl · narr_en.json · shots.json)"""
import ast, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
JEV = os.path.expanduser(r"~/volcano_work/_제브")
FILES = sys.argv[sys.argv.index("--files") + 1:] if "--files" in sys.argv else []
FILES = [f for f in FILES if not f.startswith("--")]
WIN = sys.argv[sys.argv.index("--win") + 1] if "--win" in sys.argv else "windows.json"
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
EN = json.load(open("narr_en.json", encoding="utf-8")); SH = json.load(open("shots.json", encoding="utf-8"))
A = [json.loads(l) for l in open("jev_np_out.jsonl", encoding="utf-8")]
bad_n = sorted({int(a["id"].split("_")[0][1:]) for a in A if a["answers"]["contradicts"] >= 0.6 and a["answers"]["shows_narrated"] < 0.3})
kn = {}; ni = 0
for k, x in enumerate(S):
    if x[0] == "N": ni += 1; kn[ni] = k
def rngs(x): return x[2] if isinstance(x[2], list) else [(x[2], x[3])]
items = []; cand = {}
for n in bad_n:
    x = S[kn[n]]; sh = [s for s in SH if any(s["s"] < b and s["e"] > a for a, b in rngs(x)) and s.get("desc")]
    cand[n] = sh
    for s in sh: items.append({"id": f"n{n:04d}_s{s['i']}", "narration": EN.get(str(n), x[1]), "shot": s["desc"]})
fi, fo = "jev_nn_in.jsonl", "jev_nn_out.jsonl"
with open(fi, "w", encoding="utf-8") as f:
    for it in items: f.write(json.dumps(it, ensure_ascii=False) + "\n")
r = subprocess.run(["py", "-3.12", rf"{JEV}\거르기.py", "--spec", rf"{JEV}\나레그림_맞음.json", "--in", fi, "--out", fo])
if r.returncode == 2: print("★제브 거부로 멈춤 — 다시 돌리면 이어서"); sys.exit(2)
J = {json.loads(l)["id"]: json.loads(l)["answers"] for l in open(fo, encoding="utf-8")}
new = {}; manual = []
for n in bad_n:
    x = S[kn[n]]; sh = sorted(cand[n], key=lambda s: s["s"])
    ok = [J.get(f"n{n:04d}_s{s['i']}", {}) for s in sh]
    good = [i for i, o in enumerate(ok) if o.get("shows_narrated", 0) >= 0.5 and o.get("contradicts", 1) < 0.5]
    if not good: manual.append(f"n{n:04d} {x[1]}  구간 {rngs(x)} · 맞는 컷 없음"); continue
    need = len(re.sub(r"\s", "", x[1])) / 6.5 * 2.2
    keep = set(good)
    def span(): return sum(min(sh[i]["e"], max(b for a, b in rngs(x))) - max(sh[i]["s"], min(a for a, b in rngs(x))) for i in keep)
    while span() < need:
        nb = sorted({j for i in keep for j in (i - 1, i + 1) if 0 <= j < len(sh) and j not in keep and ok[j].get("contradicts", 1) < 0.5},
                    key=lambda j: -ok[j].get("shows_narrated", 0))
        if not nb: break
        keep.add(nb[0])
    lo, hi = min(a for a, b in rngs(x)), max(b for a, b in rngs(x))
    runs = []
    for i in sorted(keep):
        a, b = max(sh[i]["s"], lo), min(sh[i]["e"], hi)
        if runs and a - runs[-1][1] < 0.6: runs[-1][1] = b
        else: runs.append([a, b])
    runs = [(round(a, 1), round(b, 1)) for a, b in runs if b - a >= 1.0]
    if not runs or sum(b - a for a, b in runs) < need * 0.8: manual.append(f"n{n:04d} {x[1]}  구간 {rngs(x)} · 맞는 컷 {len(good)} 짧음"); continue
    if runs != [tuple(r) for r in rngs(x)]: new[x[1]] = runs
# 대본 원본 파일 고침
hit = 0
for p in FILES:
    L = open(p, encoding="utf-8").read().split("\n"); ch = 0
    for i, line in enumerate(L):
        m = re.match(r'\s*\("N",\s*"((?:[^"\\]|\\.)*)"', line)
        if not m or m.group(1) not in new: continue
        body = line.strip().rstrip(",")
        t = ast.literal_eval(body); runs = new[t[1]]
        opt = [t[-1]] if isinstance(t[-1], dict) else []
        rg = [f"{runs[0][0]}, {runs[0][1]}"] if len(runs) == 1 else ["[" + ", ".join(f"({a}, {b})" for a, b in runs) + "]"]
        L[i] = "(" + ", ".join(['"N"', json.dumps(t[1], ensure_ascii=False)] + rg + [repr(o) for o in opt]) + "),"; ch += 1
    if ch: open(p, "w", encoding="utf-8").write("\n".join(L)); hit += ch
    print(p, "고침", ch)
open("np_narrow_manual.txt", "w", encoding="utf-8").write("\n".join(manual) + "\n")
print("걸린 줄", len(bad_n), "· 좁힘", len(new), "· 파일에서 고침", hit, "· 손으로 볼 것", len(manual), "→ np_narrow_manual.txt")
