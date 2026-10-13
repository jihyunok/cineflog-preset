# -*- coding: utf-8 -*-
"""건네기 전 전 구간 자동 검사 (10-13 "내가 이런거 다 일일이 찾아보고얘기해야해? / 어디까지 다 뒤져서 말해야 되니").
① 대사 자막 ↔ 실제 영어 말소리(src_words.json) ② 나레·대사 없는 3초+ 틈 ③ 나레 밑 그림이 벤치와 다른 장면인 창 ④ 3초 간격 ⑥ 0.5초 안 되는 깜빡 컷
나레 자막 ↔ 목소리는 subcheck.py 로 따로. 사용: python check_all.py windows_v8.json subs_v8.ass"""
import json, sys, numpy as np
WN = json.load(open(sys.argv[1], encoding="utf-8")); ASS = sys.argv[2]
SPD, GAP = 1.05, 3.0
E = json.load(open("edl.json")); SW = json.load(open("src_words.json", encoding="utf-8"))
PL = json.load(open("narr_place.json")); NAR = sorted((q["t"], q["t"] + q["d"]) for q in PL)
def src_at(t):
    g = next((g for g in E if g["b0"] <= t < g["b1"]), E[-1]); return g["s0"] + (t - g["b0"])
def slen(w): return (w["b"] - w["a"] - w.get("hold", 0)) * (w.get("rate", SPD) if w["kind"] == "A" else 1)
def ts(x):
    h, m, s = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
subs = [(ts(l.split(",")[1]), ts(l.split(",")[2]), l.rstrip("\n").split(",", 9)[9]) for l in open(ASS, encoding="utf-8") if l.startswith("Dialogue") and ",D,," in l]
# ①
bad1 = []
for w in WN:
    if w["kind"] != "D": continue
    ws = [x for x in SW if w["s"] - 0.3 <= x[0] < w["s"] + slen(w) - 0.2]
    st = [a for a, b, t in subs if w["a"] - 0.01 <= a < w["b"]]
    if not ws or not st: continue
    voice = w["a"] + (ws[0][0] - w["s"]); d = st[0] - voice
    lastv = w["a"] + (max(x[1] for x in ws) - w["s"])
    if abs(d) > 0.4 or lastv > w["b"] + 0.05: bad1.append((mm(w["a"]), round(d, 2), round(lastv - w["b"], 2), w.get("ko")))
print(f"① 대사 자막↔말소리 0.4초+ 어긋남/말 잘림: {len(bad1)}")
for b in bad1: print("  ", b)
# ②
iv = sorted(NAR + [(w["a"], w["b"]) for w in WN if w["kind"] == "D"]); e = 0; g = []
for a, b in iv:
    if a - e > 3.0: g.append((mm(e), round(a - e, 1)))
    e = max(e, b)
print(f"② 나레·대사 없는 3초+ 틈: {len(g)}곳 {sum(x[1] for x in g):.0f}초 · 5초+ {[x for x in g if x[1] >= 5]}")
# ③
FA = np.load("fp_src.npy").astype(np.float32); HQ = np.sort(FA.reshape(len(FA), -1), 1)[:, ::27] / 255
def fi(t): return min(int(t * 4), len(HQ) - 1)
bad3 = []
for w in WN:
    if w["kind"] != "A" or not any(w["a"] < y and w["b"] > x for x, y in NAR): continue
    m = (w["a"] + w["b"]) / 2; v = np.abs(HQ[fi(w["s"] + slen(w) / 2)] - HQ[fi(src_at(m))]).mean()
    if v > 0.15: bad3.append((mm(w["a"]), round(float(v), 2)))
print(f"③ 나레 밑인데 벤치와 다른 장면 같은 창: {len(bad3)} {bad3[:30]}")
# ④
def zone(t): return "hook" if t < 84.6 else "crit" if t >= 1592 else "main"
close = 0
for z in ("hook", "main", "crit"):
    sp = sorted([(w["s"], w["s"] + slen(w)) for w in WN if zone(w["a"]) == z] + [(w["vs"], w["vs"] + slen(w)) for w in WN if zone(w["a"]) == z and "vs" in w])
    close += sum(1 for i in range(len(sp) - 1) if sp[i + 1][0] - sp[i][1] < GAP - 0.01)
print(f"④ 3초 간격 어김: {close} · 창 최장 {max(w['b'] - w['a'] for w in WN):.2f}초")
# ⑥ 깜빡 컷 (10-13): 0.5초 안 되는 창 — 좌우반전 액션 컷이면 더 튄다. fix4_v8.py 처럼 앞뒤 창에 붙이기(★hold 금지 — ⑦)
fl = [(mm(w["a"]), round(w["b"] - w["a"], 2), w["kind"]) for w in WN if w["b"] - w["a"] - w.get("hold", 0) < 0.5]
print(f"⑥ 0.5초 안 되는 깜빡 컷: {len(fl)} {fl[:20]}")
# ⑦ 멈춤 (10-13 "중간에 영상이잠깐씩 멈추는것도 보이던데 왜그래?"): hold(끝 그림 멈춤)는 0 이어야. 느리게 튼 창(rate)은 0.85 아래면 눈에 띈다
ho = [(mm(w["a"]), w["hold"]) for w in WN if w.get("hold", 0) > 0.005]
rt = [(mm(w["a"]), w["rate"]) for w in WN if "rate" in w]
print(f"⑦ 멈춤 창: {len(ho)} {ho[:10]} · 느리게 튼 창 {len(rt)} · 가장 느림 {min([r for _, r in rt], default=None)} · 0.85 아래 {[x for x in rt if x[1] < 0.85]}")
