# -*- coding: utf-8 -*-
"""v8 창 고침 ③ — 나레 밑인데 벤치와 다른 장면인 액션 창을, 3/3 간격을 지키는 빈 원본 자리 중 벤치 그 순간 그림과 가장 닮은 곳으로 옮긴다.
10-13 "2분15초부분에 나래이션이랑 영상이랑 안맞아 그뒤" 뒤 2:17~2:23 이 남아 있었다(창고 장면 원본이 3/3 때문에 모자라 바깥 장면으로 넘어감).
사용: python fix3_v8.py [반경초=90] → windows_v8.json 고쳐 쓰고(옛 것은 windows_v8_pre3.json), 바뀐 창의 clips_v8/cNNNN.mkv 를 지운다 → build_v8.py cut → build_v8.py"""
import json, os, shutil, sys, numpy as np
SPD, GAP, LO, SRCLEN, ST = 1.05, 3.0, 62.0, 6939.6, 0.05
RAD = float(sys.argv[1]) if len(sys.argv) > 1 else 90
W = json.load(open("windows_v8.json", encoding="utf-8")); E = json.load(open("edl.json"))
PL = json.load(open("narr_place.json")); NAR = sorted((q["t"], q["t"] + q["d"]) for q in PL)
FA = np.load("fp_src.npy").astype(np.float32)
HQ = np.sort(FA.reshape(len(FA), -1), 1)[:, ::27] / 255; CQ = FA.reshape(len(FA), 3, 6, 6, 8).mean((2, 4)).reshape(len(FA), -1) / 255; del FA
def src_at(t):
    g = next((g for g in E if g["b0"] <= t < g["b1"]), E[-1]); return g["s0"] + (t - g["b0"])
def fi(t): return int(np.clip(t * 4, 0, len(HQ) - 1))
def slen(w): return (w["b"] - w["a"] - w.get("hold", 0)) * (SPD if w["kind"] == "A" else 1)
def zone(t): return "hook" if t < 84.6 else "crit" if t >= 1592 else "main"
def under(w): return any(w["a"] < y and w["b"] > x for x, y in NAR)
def mid_d(s, w):   # check_all ③ 과 같은 잣대(가운데 한 장)
    return float(np.abs(HQ[fi(s + slen(w) / 2)] - HQ[fi(src_at((w["a"] + w["b"]) / 2))]).mean())
def cost(s, w):    # 세 군데(20·50·80%) 밝기 분포 + 배치
    L = slen(w); c = 0
    for f in (0.2, 0.5, 0.8):
        i, j = fi(s + L * f), fi(src_at(w["a"] + (w["b"] - w["a"]) * f))
        c += np.abs(HQ[i] - HQ[j]).mean() + 0.5 * np.abs(CQ[i] - CQ[j]).mean()
    return c / 3
if not os.path.exists("windows_v8_pre3.json"): shutil.copy("windows_v8.json", "windows_v8_pre3.json")
bad = [k for k, w in enumerate(W) if w["kind"] == "A" and under(w) and mid_d(w["s"], w) > 0.15]
print("고칠 창", len(bad))
moved = []
for k in sorted(bad, key=lambda k: -mid_d(W[k]["s"], W[k])):
    w = W[k]; L = slen(w); z = zone(w["a"]); want = src_at((w["a"] + w["b"]) / 2) - L / 2
    oth = [(x["s"], x["s"] + slen(x)) for j, x in enumerate(W) if j != k and zone(x["a"]) == z]
    best = (cost(w["s"], w), w["s"])
    for c in np.arange(max(LO, want - RAD), min(SRCLEN - L, want + RAD), ST):
        if any(c < e + GAP and c + L + GAP > s for s, e in oth): continue
        v = cost(c, w)
        if v < best[0]: best = (v, round(float(c), 3))
    old = mid_d(w["s"], w); new = mid_d(best[1], w)
    if best[1] != w["s"] and new < old * 0.7:
        moved.append((k, w["a"], w["s"], best[1], round(old, 2), round(new, 2))); w["s"] = best[1]
        p = f"clips_v8/c{k:04d}.mkv"
        if os.path.exists(p): os.remove(p)
for m in moved: print(f"  창{m[0]} {int(m[1]//60)}:{m[1]%60:04.1f} 원본 {m[2]:.1f}→{m[3]:.1f} · 다름 {m[4]}→{m[5]}")
json.dump(W, open("windows_v8.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(W, open("clips_v8_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)   # 10-13 fix4~6 캐시 번호표
left = [k for k, w in enumerate(W) if w["kind"] == "A" and under(w) and mid_d(w["s"], w) > 0.15]
print("옮김", len(moved), "· 남은 다른 장면", len(left), [f"{int(W[k]['a']//60)}:{W[k]['a']%60:04.1f}" for k in left])
