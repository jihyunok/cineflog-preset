# -*- coding: utf-8 -*-
"""나레 조각 경계 다시 자르기 (10-13 "4분54초에 고 가 따로 붙어있어" / "8분12초 그 곳까지 이렇게 나와" / "왜자꾸 이런게 나오는거야").
gem_split 은 받아쓰기 낱말 끝 시각(0.1~0.3초 이르게 나옴)에서 잘라, 앞 문장 끝 글자 꼬리가 다음 조각 맨 앞에(「있었고」→「…있었」+「고」),
또는 다음 문장 첫 글자 머리가 앞 조각 끝에(「뿐.」+「그」 / 「곳까지」) 따로 붙었다. 원본 wav 소리 크기(10ms)로 경계를 다시 잡는다:
 R3 경계가 0.2초+ 쉼 안이면 그대로(토막 없음)
 R1 경계 뒤 0.35초 안 짧은 소리 토막이 0.2초+ 쉼으로 끝나면 → 그 토막은 앞 문장 끝 → 그 쉼 가운데로 (다음 조각이 「그때,」처럼 짧은 낱말+쉼표로 시작하면 0.15초 안만)
 R2 경계 앞 0.15초 안 소리 토막이 0.2초+ 쉼 뒤에 있으면 → 다음 문장 머리 → 그 앞 쉼 가운데로
 R4 그 밖에 소리 속이면 ±0.12초 안 가장 조용한 곳
118 은 118+119 를 이어 붙인 조각(SKIP 119)이라 src 를 117|118 ~ 119|120 으로 본다.
사용: python narr_recut.py [--dry]  → 바뀐 조각 wav 다시 자르고(옛 것 narr/_pre_recut/), _asr.json 지움 → 다음에 realign.py"""
import json, glob, os, re, shutil, subprocess, sys, numpy as np
SR = 16000; HOP = 0.01; DRY = "--dry" in sys.argv
def load(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.float32)
def env_db(x):
    n = int(HOP * SR); m = len(x) // n
    return 20 * np.log10(np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(1) + 1e-12))
def gaps(db, thr=-40, mind=0.08):
    s = db < thr; out = []; i = 0
    while i < len(s):
        if s[i]:
            j = i
            while j < len(s) and s[j]: j += 1
            if (j - i) * HOP >= mind: out.append((round(i * HOP, 2), round(j * HOP, 2)))
            i = j
        else: i += 1
    return out
P = {}
for p in sorted(glob.glob("narr/n[0-9][0-9][0-9].json")):
    P[int(p[6:9])] = json.load(open(p, encoding="utf-8"))
SRC = {i: list(d["src"]) for i, d in P.items()}
SRC[118] = [SRC[118][0], SRC[118][1], SRC[119][2]]; del SRC[119]       # 118 = 118+119
ids = sorted(SRC); cache = {}
def G(w):
    if w not in cache: db = env_db(load(w)); cache[w] = (db, gaps(db))
    return cache[w]
def short_lead(text):                       # 「그때,」「결국」처럼 짧은 낱말 + 쉼표/끝
    m = re.match(r"\s*(\S{1,3}?)[,.]", text); return bool(m) or len(re.sub(r"\W", "", text)) <= 3
new = {}; log = []
for i, j in zip(ids, ids[1:]):
    a, b = SRC[i], SRC[j]
    if a[0] != b[0] or abs(a[2] - b[1]) > 0.01: continue
    db, gp = G(a[0]); t = a[2]
    LG = [g for g in gp if g[1] - g[0] >= 0.2]
    gin = next((g for g in gp if g[0] - 0.005 <= t <= g[1] + 0.005), None)
    cut, rule = t, ""
    if gin and gin[1] - gin[0] >= 0.2:
        cut, rule = t, "R3"                 # 이미 0.2초+ 쉼 안 — 앞뒤 쉼은 silenceremove 가 깎으니 그대로 둔다
    else:
        st = gin[1] if gin else t; en = gin[0] if gin else t
        nx = min((g for g in LG if g[0] >= st - 0.005), key=lambda g: g[0], default=None)
        pv = max((g for g in LG if g[1] <= en + 0.005), key=lambda g: g[1], default=None)
        b1 = nx[0] - st if nx else 9; b2 = en - pv[1] if pv else 9
        lim1 = 0.15 if short_lead(P[j]["text"]) else 0.35
        c1 = b1 < lim1; c2 = b2 < 0.15
        if c1 and (not c2 or b1 <= b2): cut, rule = (nx[0] + nx[1]) / 2, f"R1 뒤 토막 {b1:.2f}"
        elif c2: cut, rule = (pv[0] + pv[1]) / 2, f"R2 앞 토막 {b2:.2f}"
        else:
            k = int(round(t / HOP))
            if db[max(0, k - 1):k + 2].max() > -40:
                lo, hi = max(1, k - 12), min(len(db) - 2, k + 12)
                sm = np.convolve(db, np.ones(3) / 3, "same")
                q = lo + int(np.argmin(sm[lo:hi + 1]))
                if sm[q] < sm[k] - 1: cut, rule = q * HOP, f"R4 조용한 곳 {sm[k]:.0f}→{sm[q]:.0f}dB"     # 이미 가장 조용한 곳이면 그대로(두 번 돌려도 같게)
    if abs(cut - t) > 0.03:
        new[(i, j)] = round(cut, 3)
        log.append(f"n{i:03d}|n{j:03d} {a[0][4:]} {t:.2f} → {cut:.2f} ({cut - t:+.2f}) {rule}  …{P[i]['text'][-10:]} / {P[j]['text'][:10]}…")
# R5 앞 조각이 다른 wav(다시 녹음한 7·8·75·76)라 이어지지 않는 조각 머리 / 뒤 조각이 다른 wav 인 조각 꼬리: 옛 이웃 문장 토막(n009 맨 앞 0.12초)
edge = {}
for k, i in enumerate(ids):
    w, a0, b0 = SRC[i]; db, gp = G(w); LG = [g for g in gp if g[1] - g[0] >= 0.2]
    pi = ids[k - 1] if k else None; ni = ids[k + 1] if k + 1 < len(ids) else None
    if a0 > 0.05 and (pi is None or SRC[pi][0] != w or abs(SRC[pi][2] - a0) > 0.01):
        gin = next((g for g in gp if g[0] - 0.005 <= a0 <= g[1] + 0.005), None)
        if not (gin and gin[1] - gin[0] >= 0.2):
            st = gin[1] if gin else a0; nx = min((g for g in LG if g[0] >= st - 0.005), key=lambda g: g[0], default=None)
            if nx and nx[0] - st < (0.15 if short_lead(P[i]["text"]) else 0.35):
                edge[(i, 1)] = round((nx[0] + nx[1]) / 2, 3); log.append(f"n{i:03d} 머리 {a0:.2f} → {edge[(i, 1)]:.2f} R5 앞 토막 {nx[0] - st:.2f}")
    if ni is None or SRC[ni][0] != w or abs(SRC[ni][1] - b0) > 0.01:
        gin = next((g for g in gp if g[0] - 0.005 <= b0 <= g[1] + 0.005), None)
        if not (gin and gin[1] - gin[0] >= 0.2) and b0 < len(db) * HOP - 0.05:
            en = gin[0] if gin else b0; pv = max((g for g in LG if g[1] <= en + 0.005), key=lambda g: g[1], default=None)
            if pv and en - pv[1] < 0.15:
                edge[(i, 2)] = round((pv[0] + pv[1]) / 2, 3); log.append(f"n{i:03d} 꼬리 {b0:.2f} → {edge[(i, 2)]:.2f} R5 뒤 토막 {en - pv[1]:.2f}")
print("\n".join(log)); print("바꿀 경계", len(new), "· 이어지지 않는 끝", len(edge))
if DRY: sys.exit()
SRCONLY = "--src-only" in sys.argv      # wav 는 이미 잘랐고 json 의 src 만 맞출 때(realign 이 .bak 의 옛 src 로 덮었던 것) — 경계만, R5 는 안 함
if SRCONLY: edge = {}
for (i, j), c in new.items(): SRC[i][2] = c; SRC[j][1] = c
for (i, e), c in edge.items(): SRC[i][e] = c
os.makedirs("narr/_pre_recut", exist_ok=True)
changed = sorted({i for k in new for i in k} | {i for i, _ in edge})
if not changed: sys.exit("바꿀 것 없음")
for i in changed:
    w = f"narr/n{i:03d}.wav"; d = P[i]; s = SRC[i]
    if not SRCONLY:
        for f in (w, f"narr/n{i:03d}.json", f"narr/n{i:03d}_asr.json"):
            if os.path.exists(f) and not os.path.exists(f"narr/_pre_recut/{os.path.basename(f)}"): shutil.copy(f, f"narr/_pre_recut/{os.path.basename(f)}")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s[1]:.3f}", "-to", f"{s[2]:.3f}", "-i", s[0], "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000",
                        "-ac", "2", w], check=True)
        if os.path.exists(f"narr/n{i:03d}_asr.json"): os.remove(f"narr/n{i:03d}_asr.json")
    d["src"] = [s[0], round(s[1], 3), round(s[2], 3)]
    json.dump(d, open(f"narr/n{i:03d}.json", "w", encoding="utf-8"), ensure_ascii=False)
old = json.load(open("narr_recut_changed.json")) if os.path.exists("narr_recut_changed.json") else []
json.dump(sorted(set(old) | set(changed)), open("narr_recut_changed.json", "w"))
print("다시 자른 조각", len(changed), changed)
