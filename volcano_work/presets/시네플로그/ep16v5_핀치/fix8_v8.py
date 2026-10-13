# -*- coding: utf-8 -*-
"""v8 여덟째 손질 (10-13 "제브사용해") — 제브 나레 판정(나레그림_맞음.json)에서 «벤치 그림은 나레와 맞는데 우리 그림만 어긋남»인 나레 밑 창을,
3초 간격을 지키는 빈자리(벤치 자리 ±R초) 후보 컷들 중 제브가 나레와 가장 맞다고 본 컷으로 옮긴다(고르기는 제브, 결정은 코드).
입력: jev_narr_in.jsonl / jev_narr_out.jsonl (o=우리, b=벤치), shots.json(agy 컷 설명), narr_en.json.
사용: python fix8_v8.py [R=40] → windows_v8.json (옛 것 windows_v8_pre8.json), 캐시 번호표 clips_v8_index.json"""
import json, os, shutil, subprocess, sys, numpy as np
R = float(sys.argv[1]) if len(sys.argv) > 1 else 40
SPD, GAP, ST = 1.05, 3.0, 0.25
JEV = r"C:\Users\uere\volcano_work\_제브"
W = json.load(open("windows_v8.json", encoding="utf-8"))
if not os.path.exists("windows_v8_pre8.json"): shutil.copy("windows_v8.json", "windows_v8_pre8.json")
E = json.load(open("edl.json")); PL = json.load(open("narr_place.json")); EN = json.load(open("narr_en.json", encoding="utf-8"))
SH = json.load(open("shots.json", encoding="utf-8"))
def src_at(t):
    g = next((g for g in E if g["b0"] <= t < g["b1"]), E[-1]); return g["s0"] + (t - g["b0"])
def slen(w): return (w["b"] - w["a"] - w.get("hold", 0)) * (SPD if w["kind"] == "A" else 1)
def zone(t): return "hook" if t < 84.6 else "crit" if t >= 1592 else "main"
def shot_of(t): return next((x for x in SH if x["s"] <= t < x["e"]), SH[-1])
RO = {json.loads(l)["id"]: json.loads(l)["answers"] for l in open("jev_narr_out.jsonl", encoding="utf-8")}
flag = sorted(int(k[1:]) for k in RO if k[0] == "o" and RO[k]["contradicts"] >= 0.5 and RO["b" + k[1:]]["contradicts"] < 0.5)
print("고칠 창", len(flag))
def narr_of(w):
    o, ni = max((min(w["b"], q["t"] + q["d"]) - max(w["a"], q["t"]), q["ni"]) for q in PL); return EN[str(ni)]
def free_starts(k):
    w = W[k]; L = slen(w); t = src_at((w["a"] + w["b"]) / 2) - L / 2; z = zone(w["a"])
    oth = [(x["s"], x["s"] + slen(x)) for j, x in enumerate(W) if j != k and zone(x["a"]) == z]
    c = np.arange(max(62.0, t - R), t + R, ST)
    ok = np.ones(len(c), bool)
    for s, e in oth: ok &= ~((c < e + GAP) & (c + L + GAP > s))
    return t, L, c[ok]
# 후보: 창마다 빈자리를 컷으로 묶어 컷마다 벤치 자리에 가장 가까운 시작 하나
cands = {}; items = []
for k in flag:
    t, L, cs = free_starts(k); by = {}
    for c in cs:
        sh = shot_of(c + L / 2)
        if sh["i"] not in by or abs(c - t) < abs(by[sh["i"]] - t): by[sh["i"]] = float(c)
    cands[k] = by
    for i, c in by.items():
        items.append({"id": f"k{k:04d}_{i:04d}", "narration": narr_of(W[k]), "shot": SH[i].get("desc", "")})
with open("jev_fix8_in.jsonl", "w", encoding="utf-8") as f:
    for it in items: f.write(json.dumps(it, ensure_ascii=False) + "\n")
if os.path.exists("jev_fix8_out.jsonl"): os.remove("jev_fix8_out.jsonl")
r = subprocess.run(["py", "-3.12", rf"{JEV}\거르기.py", "--spec", rf"{JEV}\나레그림_맞음.json", "--in", "jev_fix8_in.jsonl", "--out", "jev_fix8_out.jsonl"])
if r.returncode not in (0, 1): sys.exit(f"제브 실패 {r.returncode}")
A = {json.loads(l)["id"]: json.loads(l)["answers"] for l in open("jev_fix8_out.jsonl", encoding="utf-8")}
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
moved = 0
for k in flag:
    cur = RO[f"o{k:04d}"]; best = None
    for i, c in cands[k].items():
        a = A.get(f"k{k:04d}_{i:04d}")
        if not a or a["contradicts"] >= 0.5: continue
        sc = a["shows_narrated"] - a["contradicts"]
        if sc > cur["shows_narrated"] - cur["contradicts"] + 0.1 and (best is None or sc > best[0]): best = (sc, c, i)
    if not best: print(f"  {mm(W[k]['a'])} 더 맞는 빈자리 없음"); continue
    t, L, cs = free_starts(k)                                     # 앞에서 옮긴 창 때문에 막혔는지 다시
    if not np.any(np.abs(cs - best[1]) < 1e-6): print(f"  {mm(W[k]['a'])} 후보가 막힘"); continue
    print(f"  {mm(W[k]['a'])} 원본 {W[k]['s']:.1f} → {best[1]:.1f} (벤치 {t:.1f}) | {SH[best[2]]['desc'][:70]}")
    W[k]["s"] = round(best[1], 3); moved += 1
print("옮김", moved)
for z in ("hook", "main", "crit"):
    sp = sorted((w["s"], w["s"] + slen(w)) for w in W if zone(w["a"]) == z)
    assert not [1 for i in range(len(sp) - 1) if sp[i + 1][0] - sp[i][1] < GAP - 0.01], z
json.dump(W, open("windows_v8.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
# 캐시: 바뀐 창의 클립 지우고 번호표 갱신(창 수는 같음)
CUR = json.load(open("clips_v8_index.json", encoding="utf-8"))
for j, w in enumerate(W):
    if j >= len(CUR) or abs(CUR[j]["s"] - w["s"]) > 1e-6 or abs(CUR[j]["a"] - w["a"]) > 1e-6:
        p = f"clips_v8/c{j:04d}.mkv"
        if os.path.exists(p): os.remove(p)
json.dump(W, open("clips_v8_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
