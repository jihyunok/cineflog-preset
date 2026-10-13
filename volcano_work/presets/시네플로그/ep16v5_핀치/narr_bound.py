# -*- coding: utf-8 -*-
"""나레 조각 경계 검사 (10-13 "4분54초에 고 가 따로 붙어있어" / "8분12초 그 곳까지 이렇게 나와" / "왜자꾸 이런게 나오는거야").
gem_split 이 한 번에 뽑은 긴 wav 를 받아쓰기 낱말 시각으로 잘랐는데, 낱말 끝 시각이 틀려 경계가 소리 한가운데 떨어진 곳이 있었다
→ 앞 문장 끝 글자(「있었고」의 「고」)가 반 토막 나 다음 조각 맨 앞에 따로 붙었다.
여기선 원본 wav 소리 크기(10ms)로 경계마다: 경계가 소리 속인가, 경계 뒤·앞 짧은 소리 토막(0.45초 미만)이 긴 쉼으로 떨어져 있나.
사용: python narr_bound.py → 의심 경계 목록 (조각 번호 쌍, 경계 시각, 제안 경계)"""
import json, glob, subprocess, numpy as np
SR = 16000; HOP = 0.01
def load(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.float32)
def env_db(x):
    n = int(HOP * SR); m = len(x) // n
    r = np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(1) + 1e-12); return 20 * np.log10(r)
def gaps(db, thr=-40, mind=0.12):
    s = db < thr; out = []; i = 0
    while i < len(s):
        if s[i]:
            j = i
            while j < len(s) and s[j]: j += 1
            if (j - i) * HOP >= mind: out.append((i * HOP, j * HOP))
            i = j
        else: i += 1
    return out
P = {}
for p in sorted(glob.glob("narr/n[0-9][0-9][0-9].json")):
    d = json.load(open(p, encoding="utf-8")); P[int(p[6:9])] = d
ids = sorted(P); cache = {}
def G(w):
    if w not in cache: db = env_db(load(w)); cache[w] = (db, gaps(db))
    return cache[w]
sus = []
for i, j in zip(ids, ids[1:]):
    a, b = P[i]["src"], P[j]["src"]
    if a[0] != b[0] or abs(a[2] - b[1]) > 0.01: continue
    db, gp = G(a[0]); t = a[2]; k = int(t / HOP)
    loud = db[max(0, k - 2):k + 3].max()
    nxt = min((g for g in gp if g[0] >= t - 0.005), default=None, key=lambda g: g[0])
    prv = max((g for g in gp if g[1] <= t + 0.005), default=None, key=lambda g: g[1])
    insound = loud > -40 and not any(g[0] <= t <= g[1] for g in gp)
    after = (nxt[0] - t) if nxt else 9; before = (t - prv[1]) if prv else 9
    why = []
    if insound: why.append(f"소리 속({loud:.0f}dB)")
    if after < 0.45 and nxt and nxt[1] - nxt[0] >= 0.2 and not any(g[0] <= t <= g[1] for g in gp): why.append(f"경계 뒤 {after:.2f}초 토막")
    if before < 0.45 and prv and prv[1] - prv[0] >= 0.2 and not any(g[0] <= t <= g[1] for g in gp): why.append(f"경계 앞 {before:.2f}초 토막")
    if why:
        sus.append((i, j, a[0], t, why, prv, nxt))
        print(f"n{i:03d}|n{j:03d} {a[0][4:]} {t:.2f} {' '.join(why)} | 앞쉼 {prv} 뒤쉼 {nxt}")
        print(f"    끝: …{P[i]['text'][-12:]}  / 앞: {P[j]['text'][:12]}…")
print("의심 경계", len(sus))
json.dump([{"i": s[0], "j": s[1], "wav": s[2], "t": s[3], "why": s[4], "prv": s[5], "nxt": s[6]} for s in sus], open("narr_bound.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
