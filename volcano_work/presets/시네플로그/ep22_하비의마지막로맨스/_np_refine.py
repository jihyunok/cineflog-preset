# -*- coding: utf-8 -*-
"""관문 ⑨ 걸린 나레 줄만 — 그 줄 구간 안의 컷(shots.json)을 전부 제브(나레그림_맞음)로 판정해 맞는 컷만 남게 구간을 좁힌다 (21 짐승들 10-21).
사용: python _np_refine.py  → script.py 고침(옛 판 script_v8_before_np.py) · _np_refine.json(줄마다 옛/새 구간)"""
import json, os, re, shutil, subprocess, importlib.util
JEV = os.path.expanduser(r"~/volcano_work/_제브")
SH = json.load(open("shots.json", encoding="utf-8")); EN = json.load(open("narr_en.json", encoding="utf-8"))
sp = importlib.util.spec_from_file_location("s", "script.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); S = m.S
R = {j["id"]: j["answers"] for j in map(json.loads, open("jev_np_out.jsonl", encoding="utf-8"))}
badn = sorted({int(i[1:4]) for i, a in R.items() if a["contradicts"] >= 0.6 and a["shows_narrated"] < 0.3})
kn = {}; ni = 0
for k, x in enumerate(S):
    if x[0] == "N": ni += 1; kn[ni] = k
def rng(x): return [tuple(r) for r in x[2]] if isinstance(x[2], list) else [(x[2], x[3])]
items = []; cand = {}
for n in badn:
    x = S[kn[n]]
    for a, b in rng(x):
        for s in SH:
            if s["e"] > a and s["s"] < b:
                iid = f"n{n:03d}_{s['s']:.1f}"; cand.setdefault(n, []).append((max(a, s["s"]), min(b, s["e"]), iid))
                items.append({"id": iid, "narration": EN[str(n)], "shot": s["desc"]})
with open("_npr_in.jsonl", "w", encoding="utf-8") as f:
    for it in {it["id"]: it for it in items}.values(): f.write(json.dumps(it, ensure_ascii=False) + "\n")
if os.path.exists("_npr_out.jsonl"): os.remove("_npr_out.jsonl")
subprocess.run(["py", "-3.12", rf"{JEV}\거르기.py", "--spec", rf"{JEV}\나레그림_맞음.json", "--in", "_npr_in.jsonl", "--out", "_npr_out.jsonl"], check=True)
J = {j["id"]: j["answers"] for j in map(json.loads, open("_npr_out.jsonl", encoding="utf-8"))}
def merge(iv):
    out = []
    for a, b in sorted(iv):
        if out and a - out[-1][1] < 0.3: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return [(round(a, 1), round(b, 1)) for a, b in out if b - a >= 1.0]
need = lambda n: len(S[kn[n]][1]) / 6.5 + 2.0
change = {}
for n in badn:
    strict = merge([(a, b) for a, b, i in cand[n] if J[i]["contradicts"] < 0.5 and J[i]["shows_narrated"] >= 0.3])
    loose = merge([(a, b) for a, b, i in cand[n] if not (J[i]["contradicts"] >= 0.6 and J[i]["shows_narrated"] < 0.3)])
    for nr in (strict, loose):
        if sum(b - a for a, b in nr) >= need(n): change[n] = nr; break
    else: change[n] = None
L = open("script.py", encoding="utf-8").read().split("\n")
shutil.copy("script.py", "script_v8_before_np.py")
log = {}
for n, nr in change.items():
    x = S[kn[n]]; old = rng(x)
    log[n] = {"text": x[1], "old": old, "new": nr}
    if not nr or nr == old: continue
    pre = "(" + json.dumps("N", ensure_ascii=False) + ", " + json.dumps(x[1], ensure_ascii=False) + ","
    ix = [i for i, l in enumerate(L) if l.startswith(pre)]; assert len(ix) == 1, (n, ix)
    l = L[ix[0]]; tail = l[l.rindex("),") + 2:] if "),   #" in l or l.rstrip().endswith("),") else ""
    opt = x[-1] if isinstance(x[-1], dict) else None
    w = f"{nr[0][0]}, {nr[0][1]}" if len(nr) == 1 else "[" + ", ".join(f"({a}, {b})" for a, b in nr) + "]"
    L[ix[0]] = f'("N", {json.dumps(x[1], ensure_ascii=False)}, {w}' + (", " + repr(opt) if opt else "") + ")," + tail
open("script.py", "w", encoding="utf-8").write("\n".join(L))
json.dump(log, open("_np_refine.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("걸린 줄", len(badn), "· 좁힘", sum(1 for n, v in change.items() if v and v != rng(S[kn[n]])), "· 맞는 컷 모자람", [n for n, v in change.items() if v is None])
