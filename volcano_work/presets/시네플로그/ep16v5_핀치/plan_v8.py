# -*- coding: utf-8 -*-
"""16 핀치 v8 창 짜기 — v7 windows.json 의 훅·끝 비평은 그대로 두고 본편(85~1592초)을 다시 짠다.
10-13 사용자:
 ① "2분15초부분에 나래이션이랑 영상이랑 안맞아 그뒤" — v7 은 창을 앞에서부터 채우며 원하는 자리 '뒤쪽'만 찾아,
    3/3 규칙(원본 소비 ≈ 화면 시간 2배) 때문에 원본 자리가 계속 밀렸다(2:15 +43초, 3분대 +25~50초).
    → 본편 액션 창 전부를 한꺼번에 DP 로 놓는다: 원하는 자리와 차이 합 최소, 3초 간격·대사 창 둘레는 금지.
 ② "2분59초 다음 대사도없고 나래도없고너무 길어" — v7 은 나레 없는 자리에 말소리 없는 원본만 골라 3초+ 빈 곳이 123곳(약 12분).
    → 나레·대사 없는 틈이 3초를 넘으면, 그 순간 벤치 원본 자리 ±30초 안의 우리 자막 있는 대사 한 줄(5.9초 이하, 3/3 지킴)을 끼운다.
사용: python plan_v8.py → windows_v8.json"""
import json, re, numpy as np
SPD, GAP, LO, MAXC, Z0, Z1 = 1.05, 3.0, 62.0, 2.9, 85.0, 1592.0
E = json.load(open("edl.json")); W7 = json.load(open("windows.json", encoding="utf-8"))
EVL = json.load(open("../ep16v4_핀치/subev.json"))
KO = json.load(open("../ep16v4_핀치/ko16.json", encoding="utf-8"))
DADD = {x["id"]: x["ko"] for x in json.load(open("dsubs.json", encoding="utf-8")) if x["ko"]}
DEND = json.load(open("../ep16v4_핀치/dend.json"))
PL = json.load(open("narr_place.json")); NAR = sorted((q["t"] - 0.25, q["t"] + q["d"] + 0.25) for q in PL)
cuts = np.array([float(x) for x in re.findall(r"pts_time:([\d.]+)", open("../ep16v4_핀치/scenes.txt").read())])
SRCLEN = 6939.6
import sys; RAD = float(sys.argv[1]) if len(sys.argv) > 1 else 30
def src_at(t):
    g = next((g for g in E if g["b0"] <= t < g["b1"]), E[-1]); return g["s0"] + (t - g["b0"])
def under(a, b): return any(a < y and b > x for x, y in NAR)
def slen(w): return (w["b"] - w["a"]) * (SPD if w["kind"] == "A" else 1)

hook = [w for w in W7 if w["a"] < Z0]; crit = [w for w in W7 if w["a"] >= Z1]
T0, T1 = hook[-1]["b"], crit[0]["a"]
D = [dict(w) for w in W7 if w["kind"] == "D" and T0 <= w["a"] < T1]
def blocked(s, e): return s < LO or any(s < w["s"] + slen(w) + GAP and e + GAP > w["s"] for w in D)

# ② 빈 틈에 대사 끼우기
# 대사 줄 시각: subev(박힌 자막이 뜬 시각) 대신 실제 영어 말소리(src_words.json, Groq) — 10-13 "5분4초 고 늦게나와"
SW = json.load(open("src_words.json", encoding="utf-8"))
def real(ev):
    ws = [w for w in SW if ev["s"] - 0.8 <= w[0] <= ev["e"] - 0.1]
    if not ws: return None
    return ws[0][0] - 0.12, max(w[1] for w in ws) + 0.25
LINES = []; RL = {}
for ev in EVL:
    ko = KO.get(str(ev["id"])) or DADD.get(ev["id"])
    if not ko: continue
    r = real(ev)
    if r: s, e = r
    else:
        s = ev["s"] - 0.05; de = DEND.get(str(ev["id"])); e = min(ev["e"] + 0.25, de + 0.35 if de else 9e9)
    RL[round(ev["s"] - 0.05, 2)] = (s, e)
    if 0.8 <= e - s <= 5.9: LINES.append((s, e, ko))
# v7 대사 창도 실제 말소리로 다시 맞춘다(화면 자리 a 는 그대로, 말 시작이 당겨진 만큼 a 도 당김 — 나레와 겹치면 그만큼 덜 당김)
for w in D:
    r = RL.get(round(w["s"], 2))
    if not r: continue
    s, e = r; e = min(e, s + 5.9); da = s - w["s"]
    a = w["a"] + min(0, da); b = a + (e - s)
    while under(a, b) and b - a > 0.8:
        if any(a < y and a > x for x, y in NAR): a += 0.05
        else: b -= 0.05
    w.update({"a": round(a, 3), "b": round(b, 3), "s": round(s + (a - (w["a"] + min(0, da))), 3)})
D.sort(key=lambda w: w["a"])
for i in range(len(D) - 1):                     # 대사 창끼리 겹치지 않게
    if D[i]["b"] > D[i + 1]["a"]: D[i]["b"] = D[i + 1]["a"]
while True:                                     # 말소리로 늘린 뒤 원본 3초 간격이 깨진 대사 창은 뒤의 것을 뺀다
    sd = sorted(D, key=lambda w: w["s"])
    bad = [(x, y) for x, y in zip(sd, sd[1:]) if y["s"] - (x["s"] + slen(x)) < GAP]
    if not bad: break
    x, y = bad[0]; D.remove(y if y["a"] > x["a"] else x)
def gaps():
    iv = sorted(NAR + [(w["a"], w["b"]) for w in D]); out = []; e = T0
    for a, b in iv + [(T1, T1)]:
        if a - e > 3.0 and e < T1: out.append((e, min(a, T1)))
        e = max(e, b)
    return out
added = 0
for _ in range(6):
    new = 0
    for ga, gb in gaps():
        room = gb - ga - 0.4
        want = src_at((ga + gb) / 2)
        c = [(abs(s - want), s, e, ko) for s, e, ko in LINES if abs(s - want) <= RAD and e - s <= room and not blocked(s, e)]
        if not c: continue
        _, s, e, ko = min(c)
        a = ga + 0.2 if gb - ga - (e - s) < 3.0 else (ga + gb - (e - s)) / 2   # 남는 틈이 3초 넘으면 가운데에
        D.append({"a": round(a, 3), "b": round(a + e - s, 3), "s": round(s, 3), "kind": "D", "ko": ko, "fill": 1}); new += 1
    added += new
    if not new: break
D.sort(key=lambda w: w["a"])

# 액션 창 나누기
A = []; t = T0
for w in D + [{"a": T1, "b": T1}]:
    while w["a"] - t > 0.05:
        L = min(MAXC, w["a"] - t)
        if w["a"] - t - L < 0.8 and w["a"] - t > MAXC: L = (w["a"] - t) / 2
        A.append({"a": round(t, 3), "b": round(t + L, 3), "kind": "A"}); t += L
    t = max(t, w["b"])

# ① DP 놓기 (0.25초 칸)
# 그림 지문(fp_src.npy, 4fps): 밝기 분포 32칸 + 3x6 배치 — 같은 장면이면 가깝다
FA = np.load("fp_src.npy").astype(np.float32); HQ = np.sort(FA.reshape(len(FA), -1), 1)[:, ::27] / 255
CQ = FA.reshape(len(FA), 3, 6, 6, 8).mean((2, 4)).reshape(len(FA), -1) / 255; del FA
TW = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0; VW = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
ST = 0.25; NP = int(SRCLEN / ST); grid = np.arange(NP) * ST
sm = np.zeros(int(SRCLEN / 0.05) + 200)
for w in SW: sm[int(w[0] / 0.05):int(w[1] / 0.05) + 1] = 1     # 실제 말소리
csum = np.concatenate([[0], np.cumsum(sm)]) * 0.05
bad = np.zeros(NP, bool)            # 대사 창 둘레(앞뒤 3초)
for w in D:
    bad |= (grid < w["s"] + slen(w) + GAP) & (grid > w["s"] - GAP - MAXC * SPD - 0.01)
for x in A:
    x["L"] = slen(x); x["t"] = src_at((x["a"] + x["b"]) / 2) - x["L"] / 2; x["open"] = not under(x["a"], x["b"])
A.sort(key=lambda x: (x["t"], x["a"]))
INF = 1e12; prev = None; back = []
for i, x in enumerate(A):
    L = x["L"]
    ok = (grid >= LO) & (grid + L <= SRCLEN)
    for w in D + crit:                                      # 이 창 길이로 대사 창(+끝 비평 창)과 3초 간격
        ok &= ~((grid < w["s"] + slen(w) + GAP) & (grid + L + GAP > w["s"]))
    cost = np.abs(grid - x["t"]) / TW
    m = np.clip(((grid + L / 2) * 4).astype(int), 0, len(HQ) - 1); tm = min(int((x["t"] + L / 2) * 4), len(HQ) - 1)
    cost = cost + VW * (np.abs(HQ[m] - HQ[tm]).mean(1) + 0.5 * np.abs(CQ[m] - CQ[tm]).mean(1))   # 그림이 그 순간 벤치 화면과 닮았나
    if x["open"]:
        i0 = np.minimum((grid / 0.05).astype(int), len(csum) - 1); i1 = np.minimum(((grid + L) / 0.05).astype(int), len(csum) - 1)
        ov = csum[i1] - csum[i0]; cost = cost + np.where(ov > 0.2, (8 + 6 * ov) / TW, 0)
    cost = np.where(ok, cost, INF)
    if prev is None: f = cost; back.append(None)
    else:
        sh = int(np.ceil((A[i - 1]["L"] + GAP) / ST))
        pm = np.minimum.accumulate(prev); am = np.zeros(NP, np.int32)
        idx = np.arange(NP); best = np.where(np.concatenate([[True], prev[1:] < pm[:-1]]), idx, 0)
        am = np.maximum.accumulate(best).astype(np.int32)
        f = np.full(NP, INF); f[sh:] = cost[sh:] + pm[:-sh]
        b = np.zeros(NP, np.int32); b[sh:] = am[:-sh]; back.append(b)
    prev = f
p = int(np.argmin(prev)); print("DP 비용", round(float(prev[p])))
for i in range(len(A) - 1, -1, -1):
    A[i]["s"] = round(p * ST, 3)
    if back[i] is not None: p = int(back[i][p])
# 장면 전환 바로 뒤로 살짝(간격 허락할 때만)
A.sort(key=lambda x: x["s"]); allw = sorted(A + D, key=lambda w: w["s"])
for j, w in enumerate(allw):
    if w["kind"] != "A": continue
    near = cuts[(cuts >= w["s"] - 0.3) & (cuts <= w["s"] + 0.3)]
    if not len(near): continue
    s2 = float(near[0]) + 0.08; L = slen(w)
    if (j == 0 or s2 >= allw[j - 1]["s"] + slen(allw[j - 1]) + GAP) and (j + 1 == len(allw) or s2 + L + GAP <= allw[j + 1]["s"]): w["s"] = round(s2, 3)

for x in A:
    for k in ("L", "t", "open"): x.pop(k, None)
WN = sorted(hook + A + D + crit, key=lambda w: w["a"])
json.dump(WN, open("windows_v8.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# 검사
def zone(t): return "hook" if t < Z0 else "crit" if t >= Z1 else "main"
close = []
for z in ("hook", "main", "crit"):
    sp = sorted([(w["s"], w["s"] + slen(w)) for w in WN if zone(w["a"]) == z])
    close += [sp[i] for i in range(len(sp) - 1) if sp[i + 1][0] - sp[i][1] < GAP - 0.01]
cont = sum(1 for i in range(len(WN) - 1) if abs(WN[i + 1]["a"] - WN[i]["b"]) > 0.02)
MA = [w for w in WN if w["kind"] == "A" and zone(w["a"]) == "main"]
dr = np.array([abs(w["s"] - (src_at((w["a"] + w["b"]) / 2) - slen(w) / 2)) for w in MA])
spk = sum(1 for w in MA if not under(w["a"], w["b"]) and any(w["s"] < x[1] - 0.1 and w["s"] + slen(w) > x[0] + 0.1 for x in SW))
D8 = [w for w in WN if w["kind"] == "D"]
iv = sorted(NAR + [(w["a"], w["b"]) for w in D8]); g = []; e = 0
for a, b in iv:
    if a - e > 3: g.append(a - e)
    e = max(e, b)
print(f"창 {len(WN)} · 액션 {len(WN) - len(D8)} · 대사 {len(D8)}(새로 {added}) · 최장 {max(w['b'] - w['a'] for w in WN):.2f}초 · 3초 간격 어김 {len(close)} · 시간축 끊김 {cont}")
vis = np.array([np.abs(HQ[min(int((w["s"] + slen(w) / 2) * 4), len(HQ) - 1)] - HQ[min(int((src_at((w["a"] + w["b"]) / 2)) * 4), len(HQ) - 1)]).mean() for w in MA if under(w["a"], w["b"])])
print(f"나레 밑 액션 창 그림 차이: 중앙 {np.median(vis):.3f} · 같은 장면급(<0.05) {100 * np.mean(vis < 0.05):.0f}% · 다른 장면급(>0.15) {100 * np.mean(vis > 0.15):.0f}%")
print(f"본편 원하던 자리와 차이: 중앙 {np.median(dr):.1f}초 · 90% {np.percentile(dr, 90):.1f}초 · 최대 {dr.max():.1f}초 · 나레 없는데 원본 말소리 걸린 창 {spk}")
print(f"나레·대사 없는 3초+ 틈: {len(g)}곳 {sum(g):.0f}초 · 최장 {max(g):.1f}초 (v7 123곳 710초)")
