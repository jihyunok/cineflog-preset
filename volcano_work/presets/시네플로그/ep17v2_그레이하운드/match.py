# -*- coding: utf-8 -*-
"""벤치 프레임(4fps)마다 원본에서 가장 닮은 프레임 찾기(좌우반전 포함) → 연속 구간(run)으로 묶기 → runs.json
run = {b0,b1: 벤치 초, s0: 원본 시작 초, rate: 원본/벤치 속도, flip, score}"""
import json, numpy as np
FPS = 4
B = np.load("fp_bench.npy"); S = np.load("fp_src.npy")
def norm(a):
    a = a.reshape(len(a), -1); a = a - a.mean(1, keepdims=True)
    n = np.linalg.norm(a, axis=1, keepdims=True); return a / np.maximum(n, 1e-3), n[:, 0]
Bn, bstd = norm(B); Bf, _ = norm(B[:, :, ::-1]); Sn, sstd = norm(S)
best = np.zeros(len(B), int); sc = np.zeros(len(B)); fl = np.zeros(len(B), bool)
for i in range(0, len(B), 512):
    for X, f in ((Bn, False), (Bf, True)):
        M = X[i:i + 512] @ Sn.T
        j = M.argmax(1); v = M[np.arange(len(j)), j]
        upd = v > sc[i:i + 512]
        best[i:i + 512][upd] = j[upd]; sc[i:i + 512][upd] = v[upd]; fl[i:i + 512][upd] = f
flat = bstd < 40          # 거의 단색(검은 화면·글자 카드)
np.save("match_best.npy", np.stack([best, sc, fl, flat]))
# run 묶기: 원본 프레임이 벤치와 같이 1씩(±1) 늘어나면 같은 run
runs = []; cur = None
for i in range(len(B)):
    ok = sc[i] > 0.85 and not flat[i]
    if cur and ok and cur["ok"] and fl[i] == cur["flip"] and 0 <= best[i] - cur["last"] <= 3 and abs((best[i] - cur["j0"]) - (i - cur["i0"])) <= 3:
        cur["last"] = best[i]; cur["i1"] = i; cur["sc"].append(sc[i]); continue
    if cur: runs.append(cur)
    cur = {"i0": i, "i1": i, "j0": best[i], "last": best[i], "flip": bool(fl[i]), "sc": [sc[i]], "ok": ok}
runs.append(cur)
out = []
for r in runs:
    n = r["i1"] - r["i0"] + 1
    out.append({"b0": r["i0"] / FPS, "b1": (r["i1"] + 1) / FPS, "s0": r["j0"] / FPS, "s1": (r["last"] + 1) / FPS,
                "flip": r["flip"], "score": round(float(np.mean(r["sc"])), 3), "ok": bool(r["ok"]) and n >= 2})
json.dump(out, open("runs.json", "w"), indent=0)
good = [r for r in out if r["ok"]]
print("bench frames", len(B), "runs", len(out), "good", len(good), "cover", round(sum(r["b1"] - r["b0"] for r in good), 1), "s of", len(B) / FPS)
print("flipped", sum(r["flip"] for r in good), "rate~", np.median([(r["s1"] - r["s0"]) / (r["b1"] - r["b0"]) for r in good if r["b1"] - r["b0"] > 3]))
