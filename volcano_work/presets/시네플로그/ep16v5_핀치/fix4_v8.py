# -*- coding: utf-8 -*-
"""v8 넷째 손질 (10-13) — 전 구간 검사(check_all ②)에서 남은 5초+ 빈 틈 중 벤치가 나레 없이 대사를 흘린 자리 + 0.2초 깜빡 컷.
① 훅 0:38~1:04: 3/3 때문에 원본이 벤치보다 12~18초 앞서 갔다(벤치 1:02 「15m, 최대한 주의」 자리에 우리는 흐린 화면).
   원본 1초마다 본 뒤 다시 짬: N4 「로봇은 끝까지 손을 놓지 않습니다」 밑 밖에서 버티는 로봇(2239) · N5 밑 토네이도→문 앞 로봇→차 안
   → 대사 「뭐든 꽉 잡아」 0:55.8(원본 2319.85) → 「15m, 최대한 주의」 0:59.5(원본 2334.0). 0:32.45 로봇 고도 「152m」.
② 17:53 벤치 「안 돼, 멈춰! 멈춰!」(원본 3276.6) · 21:55.8 벤치 「그들이 사라진 것 같아요」(원본 4585.25).
③ 0.5초 안 되는 액션 창(대사 창 사이 깜빡 컷, 좌우반전이라 더 튄다)은 앞이나 뒤 창에 붙인다(3/3 지킬 때만).
창 개수가 바뀌므로 clips_v8 캐시를 (a,b,s,kind) 같은 것끼리 새 번호로 옮기고 바뀐 것만 지운다.
사용: python fix4_v8.py  (windows_v8.json 을 고침, 옛 것은 windows_v8_pre4.json)"""
import json, os, shutil
SPD, GAP = 1.05, 3.0
WN = json.load(open("windows_v8.json", encoding="utf-8"))
if not os.path.exists("windows_v8_pre4.json"): shutil.copy("windows_v8.json", "windows_v8_pre4.json")
OLD = [dict(w) for w in WN]
SW = json.load(open("src_words.json", encoding="utf-8"))
PL = json.load(open("narr_place.json")); NAR = [(q["t"], q["t"] + q["d"]) for q in PL]
def slen(w): return (w["b"] - w["a"] - w.get("hold", 0)) * (SPD if w["kind"] == "A" else 1)   # hold: 끝 그림 멈춤(원본 안 씀)
def zone(t): return "hook" if t < 85 else "crit" if t >= 1592 else "main"
def find(a):
    k = [i for i, w in enumerate(WN) if abs(w["a"] - a) < 0.02]; assert len(k) == 1, (a, k); return k[0]

# ① 훅
i14, i22 = find(38.25), find(61.45)
assert i22 - i14 == 8 and abs(WN[i22]["b"] - 64.35) < 0.02
HOOK = [("A", 38.25, 41.15, 2301.46, None),      # 토네이도 → 문 앞 핀치 (N4 「이제 차 안으로 피해야 하지만」)
        ("A", 41.15, 44.05, 2239.0, None),       # 밖에서 버티는 로봇 (「로봇은 끝까지 손을 놓지 않습니다」)
        ("A", 44.05, 46.95, 2307.51, None),      # 토네이도 가까이 → 문 앞 로봇
        ("A", 46.95, 49.85, 2313.56, None),      # 개 → 차 안 핀치 (N5 「회오리가 … 그제야 차에 올라탑니다」)
        ("A", 49.85, 52.75, 2324.6, None),       # 차 안 로봇 → 커튼
        ("A", 52.75, 55.8, 2340.55, None),       # 헬멧 핀치 (「차가 버텨 주길 비는 것뿐이죠」)
        ("D", 55.8, 57.5, 2319.85, "뭐든 꽉 잡아"),
        ("A", 57.5, 59.5, 2346.75, None),        # 헬멧 핀치 → 흐림
        ("D", 59.5, 63.05, 2334.0, "15m, 최대한 주의"),
        ("A", 63.05, 64.35, 2351.85, None)]      # N6 「충돌까지 5초」
new = []
for k, a, b, s, ko in HOOK:
    w = {"a": a, "b": b, "s": s, "kind": k}
    if ko: w["ko"] = ko
    new.append(w)
WN[i14:i22 + 1] = new
i12 = find(32.45); WN[i12].update({"kind": "D", "s": 2287.0, "ko": "152m", "sub0": 0.2, "sub1": 1.6})   # "Five hundred feet" 2287.23~2287.99

# ② 17:53 · 21:55.8
k = find(1072.23); WN[k]["b"] = 1073.8
WN[k + 1].update({"a": 1073.8, "kind": "D", "s": 3276.6, "ko": "안 돼, 멈춰! 멈춰!", "sub0": 0.3})       # No! Stop! Stop! 3276.93~3278.65
k = find(1079.74); n = WN[k + 1]; d = WN[k]["b"] - WN[k]["a"]                                          # 그 뒤 깜빡 컷(원본 3280.25)은 새 대사와 붙으므로
assert d < 0.3 and n["kind"] == "D" and abs(n["s"] - 3307.8) < 0.01                                    # 「자외선은 가리지 않아」 앞에 붙임(원본 0.2초 앞 = "UV")
n.update({"a": WN[k]["a"], "s": round(n["s"] - d, 3), "sub0": round(n.get("sub0", 0.05) + d, 3)}); del WN[k]
k = find(1091.29); assert abs(WN[k]["s"] - 3303.0) < 0.01; WN[k]["s"] = 3302.9                       # 그래서 0.1초 앞으로 (3초 간격)
k = find(1315.82); WN[k].update({"b": 1318.15, "kind": "D", "ko": "그들이 사라진 것 같아요", "sub0": 1.2})  # they're gone. ~4587.48
WN[k + 1]["s"] = round(WN[k + 1]["s"] - (WN[k + 1]["a"] - 1318.15) * SPD, 3); WN[k + 1]["a"] = 1318.15

# ③ 깜빡 컷 붙이기
def ok(ws):
    for z in ("hook", "main", "crit"):
        sp = sorted((w["s"], w["s"] + slen(w)) for w in ws if zone(w["a"]) == z)
        if any(sp[i + 1][0] - sp[i][1] < GAP - 0.01 for i in range(len(sp) - 1)): return False
    return True
def word_in(s, e): return any(s < x[0] < e for x in SW)
def under(a, b): return any(a < y and b > x for x, y in NAR)
merged = []; i = 0
while i < len(WN):
    w = WN[i]
    if w["kind"] == "A" and w["b"] - w["a"] < 0.5 and 0 < i < len(WN) - 1:
        d = w["b"] - w["a"]; p, n = WN[i - 1], WN[i + 1]
        trial = [dict(x) for x in WN]; q = trial[i - 1]; q["b"] = w["b"]; del trial[i]
        pend = p["s"] + slen(p)
        if ok(trial) and not (p["kind"] == "D" and (word_in(pend, pend + d) or under(p["a"], w["b"]))):
            WN = trial; merged.append((round(w["a"], 2), "앞에")); continue
        trial = [dict(x) for x in WN]; q = trial[i + 1]; sp = SPD if n["kind"] == "A" else 1
        q["s"] = round(n["s"] - d * sp, 3); q["a"] = w["a"]
        if n["kind"] == "D": q["sub0"] = n.get("sub0", 0.05) + d
        del trial[i]
        if q["s"] >= 0 and ok(trial) and not (n["kind"] == "D" and (word_in(q["s"], n["s"]) or under(w["a"], n["b"]))):
            WN = trial; merged.append((round(w["a"], 2), "뒤에")); continue
        if p["kind"] == "A":            # 앞 액션 창을 늘리되 원본 끝은 그대로, 시작을 당김
            trial = [dict(x) for x in WN]; q = trial[i - 1]; q["b"] = w["b"]; q["s"] = round(p["s"] - d * SPD, 3); del trial[i]
            if q["s"] >= 0 and ok(trial): WN = trial; merged.append((round(w["a"], 2), "앞에(당김)")); continue
        if n["kind"] == "A":            # 뒤 액션 창을 앞으로 늘리되 원본 시작은 그대로, 끝이 늘어남
            trial = [dict(x) for x in WN]; q = trial[i + 1]; q["a"] = w["a"]; del trial[i]
            if ok(trial): WN = trial; merged.append((round(w["a"], 2), "뒤에(늘림)")); continue
        q = WN[i - 1]; q["b"] = w["b"]; q["hold"] = round(q.get("hold", 0) + d, 3); del WN[i]   # 마지막: 앞 창 끝 그림을 d 초 멈춤
        merged.append((round(w["a"], 2), "앞에(멈춤)")); continue
    i += 1
print("깜빡 컷:", len(merged), merged)

# 검사: 이어짐 · 3/3 · 대사 창이 나레 밑에 없음
for i in range(len(WN) - 1): assert abs(WN[i]["b"] - WN[i + 1]["a"]) < 0.005, (i, WN[i], WN[i + 1])
assert ok(WN), "3초 간격 어김"
bad = [(round(w["a"], 2), w.get("ko")) for w in WN if w["kind"] == "D" and any(w["a"] + 0.05 < y and w["b"] - 0.05 > x for x, y in NAR)]
print("나레 밑 대사 창:", bad)
json.dump(WN, open("windows_v8.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# 캐시 옮기기
def key(w): return (round(w["a"], 3), round(w["b"], 3), round(w["s"], 3), w["kind"], w.get("hold", 0))
CUR = json.load(open("clips_v8_index.json", encoding="utf-8")) if os.path.exists("clips_v8_index.json") else OLD   # 지금 캐시 번호가 가리키는 창
oldk = {key(w): i for i, w in enumerate(CUR)}
os.makedirs("clips_v8/_old", exist_ok=True)
for f in os.listdir("clips_v8"):
    if f.endswith(".mkv"): shutil.move(f"clips_v8/{f}", f"clips_v8/_old/{f}")
kept = 0
for j, w in enumerate(WN):
    o = oldk.get(key(w))
    if o is not None and os.path.exists(f"clips_v8/_old/c{o:04d}.mkv"):
        shutil.move(f"clips_v8/_old/c{o:04d}.mkv", f"clips_v8/c{j:04d}.mkv"); kept += 1
shutil.rmtree("clips_v8/_old")
print("창", len(OLD), "→", len(WN), "· 캐시 그대로", kept, "· 새로 자를 것", len(WN) - kept)
json.dump(WN, open("clips_v8_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
