# -*- coding: utf-8 -*-
"""11-05 다리 검사 — 사용자 「시청자는 이영상을 처음보는데 뭔소리야? 엥? 하면서 나가 버리지」(46 잭리처2 2:40 미행꾼 → 사만다).
원본을 크게 건너뛰거나(기본 20초 넘게, 뒤로 가도) 컷 설명의 장소·인물이 바뀌는 자리를 모두 뽑아, 그 앞 2줄·뒤 2줄(나레·자막)을 보여 준다.
흐름 검사(flow_check)는 장소 이름이 바뀔 때만 잡아서 같은 동네 안 건너뛰기를 놓쳤다 → 이건 시간 간격으로 다 잡는다.
「다리」 = 건너뛴 자리 바로 뒤(또는 바로 앞) 나레가 왜·어디로·누구를 말하는지. 뒤 줄이 D·A 로 시작하면 ★(다리 나레 없음).
사용: 작업 폴더에서 python bridge_check.py [건너뛴초=20]  (먼저 plan_v9.py --dry 로 windows_dry.json)
결과: bridge_check.txt — 줄기를 읽지 않은 검토자가 이 목록만 보고 「처음 보는 사람이 따라오나」 판단."""
import json, os, sys, re
GAP = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
W = json.load(open("windows_dry.json", encoding="utf-8"))
sh = json.load(open("shots.json", encoding="utf-8")) if os.path.exists("shots.json") else []
def desc(t):
    for x in sh:
        if x["s"] <= t < x["e"]: return x["desc"]
    return ""
def place(d):
    m = re.match(r"\s*(?:At|In|Inside|On|Outside|Aboard|Along|By|Near)\s+(?:the\s+|an?\s+)?([^,]+?)(?:\s+at night|\s+during the day|,|$)", d)
    return (m.group(1).lower() if m else "")[:40]
rng = {}
for w in W:
    if w.get("z") != "main": continue
    k = w["k"]; a = w["s"]; b = w["s"] + (w["b"] - w["a"])
    lo, hi = rng.get(k, (a, b)); rng[k] = (min(lo, a), max(hi, b))
ks = sorted(rng)
def show(k):
    x = S[k]
    t = x[1] if x[0] == "N" else (x[2] if x[0] == "D" else "(원본 소리)")
    return f"S{k} {x[0]} {t}"
out = []; n = star = 0
for i in range(1, len(ks)):
    k0, k1 = ks[i - 1], ks[i]
    e0 = rng[k0][1]; s1 = rng[k1][0]
    jump = s1 - e0
    p0, p1 = place(desc(e0 - 0.1)), place(desc(s1 + 0.1))
    why = []
    if jump > GAP: why.append(f"원본 {jump:.0f}초 건너뜀")
    if jump < -3: why.append(f"원본 {-jump:.0f}초 뒤로")
    if p0 and p1 and p0 != p1: why.append(f"장소 「{p0}」→「{p1}」")
    if not why: continue
    n += 1
    nobr = S[k1][0] != "N"
    if nobr: star += 1
    mm = lambda t: f"{int(t // 60)}:{t % 60:04.1f}"
    out.append(f"{'★' if nobr else '·'} [{n}] {mm(e0)} → {mm(s1)} · {' · '.join(why)}" + (" · ★뒤 줄이 나레 아님(다리 없음)" if nobr else ""))
    for k in ks[max(0, i - 2):i]: out.append("     " + show(k))
    out.append("   ───── 여기서 넘어감")
    for k in ks[i:i + 2]: out.append("     " + show(k))
    out.append("")
open("bridge_check.txt", "w", encoding="utf-8").write(f"다리 검사 — 넘어가는 자리 {n}곳 · ★다리 나레 없음 {star}곳 (건너뜀 기준 {GAP:.0f}초)\n\n" + "\n".join(out))
print(f"다리 검사: 넘어가는 자리 {n}곳 · ★다리 나레 없음 {star}곳 → bridge_check.txt")
