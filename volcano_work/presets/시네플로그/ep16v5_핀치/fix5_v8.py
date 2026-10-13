# -*- coding: utf-8 -*-
"""v8 다섯째 손질 (10-13) — 사용자 "1분33초까지 영상이랑 나래가 안맞아 / 왜 자꾸 산으로 가니".
원인: plan_v8 의 DP(원본 자리를 벤치 그 순간 자리에 최대한 붙임)는 본편(85초~)만 했고, 훅(0~85초)은 v7 식으로 앞에서부터 채워
원본이 벤치보다 8~20초씩 앞서 갔다. 게다가 fix4 에서 훅 일부를 내 판단으로 골랐다(0:41 밖의 로봇, 0:50~0:59) → 더 어긋남.
나레는 벤치 그림에 맞춰 쓴 것이므로, 내 판단 없이 벤치 그림을 따른다:
 - 대사 창 = 벤치가 나레 없이 흘린 대사만(dsubs under=False): 0:16 「제발, 맙소사 / 주의…」 · 0:23.6 「캠핑카로 돌아가야 해요」 ·
   0:32.3 「274m」(벤치 그대로, fix4 의 「152m」는 뺌) · 0:55.8 「뭐든 꽉 잡아」 · 0:59.5 「15m, 최대한 주의」.
 - 나머지는 액션 창(2.9초 이하)으로 나누고 plan_v8 과 같은 DP(벤치 자리와의 차이 + 그림 지문 닮음, 3초 간격)로 원본을 놓는다.
 - 1:24.65~1:35(본편 첫 창 넷)도 다시 놓는다 — 훅/본편 경계(85초) 때문에 1:24.65 창(원본 79.65)과 1:27.55 창(82.5)이
   서로 검사되지 않아 원본 5.9초가 이어졌다. 경계를 84.6초로.
사용: python fix5_v8.py → windows_v8.json (옛 것 windows_v8_pre5.json), 캐시는 clips_v8_index.json 으로 옮김."""
import json, os, re, shutil, sys, numpy as np
SPD, GAP, MAXC, ZB = 1.05, 3.0, 2.9, 84.6
TW, VW = 5.0, 20.0                       # plan_v8 을 돌린 값(python plan_v8.py 20 5 20)
NW = float(os.environ.get("NW", 4))      # 나레 밑 창은 벤치 자리와의 차이를 NW 배로 무겁게 — 나레는 벤치 그림에 맞춰 쓴 것
WN = json.load(open("windows_v8.json", encoding="utf-8"))
if not os.path.exists("windows_v8_pre5.json"): shutil.copy("windows_v8.json", "windows_v8_pre5.json")
E = json.load(open("edl.json")); SW = json.load(open("src_words.json", encoding="utf-8"))
PL = json.load(open("narr_place.json")); NAR = sorted((q["t"] - 0.25, q["t"] + q["d"] + 0.25) for q in PL)
def src_at(t):
    g = next((g for g in E if g["b0"] <= t < g["b1"]), E[-1]); return g["s0"] + (t - g["b0"])
def slen(w): return (w["b"] - w["a"] - w.get("hold", 0)) * (SPD if w["kind"] == "A" else 1)
def under(a, b): return any(a < y and b > x for x, y in NAR)
FA = np.load("fp_src.npy").astype(np.float32); HQ = np.sort(FA.reshape(len(FA), -1), 1)[:, ::27] / 255
CQ = FA.reshape(len(FA), 3, 6, 6, 8).mean((2, 4)).reshape(len(FA), -1) / 255; del FA
sm = np.zeros(int(7000 / 0.05)); csum = None
for w in SW: sm[int(w[0] / 0.05):int(w[1] / 0.05) + 1] = 1
csum = np.concatenate([[0], np.cumsum(sm)]) * 0.05
ST = 0.25; NP = int(6939.6 / ST); grid = np.arange(NP) * ST

def place(A, fixed, lo=0.0, hi=6939.6):
    """A(액션 창들)의 원본 s 를 DP 로. fixed = 3초 간격을 지켜야 할 다른 창들."""
    for x in A:
        x["L"] = slen(x); x["t"] = src_at((x["a"] + x["b"]) / 2) - x["L"] / 2; x["open"] = not under(x["a"], x["b"])
    A.sort(key=lambda x: (x["t"], x["a"]))
    INF = 1e12; prev = None; back = []
    for i, x in enumerate(A):
        L = x["L"]; ok = (grid >= lo) & (grid + L <= hi)
        for w in fixed: ok &= ~((grid < w["s"] + slen(w) + GAP) & (grid + L + GAP > w["s"]))
        cost = np.abs(grid - x["t"]) / TW * (1 if x["open"] else NW)
        m = np.clip(((grid + L / 2) * 4).astype(int), 0, len(HQ) - 1); tm = min(int((x["t"] + L / 2) * 4), len(HQ) - 1)
        cost = cost + VW * (np.abs(HQ[m] - HQ[tm]).mean(1) + 0.5 * np.abs(CQ[m] - CQ[tm]).mean(1))
        if x["open"]:
            i0 = np.minimum((grid / 0.05).astype(int), len(csum) - 1); i1 = np.minimum(((grid + L) / 0.05).astype(int), len(csum) - 1)
            ov = csum[i1] - csum[i0]; cost = cost + np.where(ov > 0.2, (8 + 6 * ov) / TW, 0)
        cost = np.where(ok, cost, INF)
        if prev is None: f = cost; back.append(None)
        else:
            sh = int(np.ceil((A[i - 1]["L"] + GAP) / ST))
            pm = np.minimum.accumulate(prev); idx = np.arange(NP)
            best = np.where(np.concatenate([[True], prev[1:] < pm[:-1]]), idx, 0); am = np.maximum.accumulate(best).astype(np.int32)
            f = np.full(NP, INF); f[sh:] = cost[sh:] + pm[:-sh]
            b = np.zeros(NP, np.int32); b[sh:] = am[:-sh]; back.append(b)
        prev = f
    p = int(np.argmin(prev)); assert prev[p] < 1e11, "놓을 자리 없음"
    for i in range(len(A) - 1, -1, -1):
        A[i]["s"] = round(p * ST, 3)
        if back[i] is not None: p = int(back[i][p])
    for x in A:
        for k in ("L", "t", "open"): x.pop(k)
    return A

NARR = [(q["t"], q["t"] + q["d"]) for q in PL]
def nsec(w): return sum(max(0, min(w["b"], y) - max(w["a"], x)) for x, y in NARR)
def narrated(w): return nsec(w) >= 0.3      # 짧은 나레(0:36 「토네이도는 이미 코앞」 1초)가 두 창에 걸쳐도 둘 다 나레 창
def place2(A, fixed, lo=0.0, hi=6939.6):
    """나레 밑 창(나레 0.3초 넘게)을 먼저 DP 로 벤치 자리에 놓고, 나레 없는 창은 남은 자리 중 가장 가까운 곳에(원본 순서 안 따짐).
    place() 하나로 하면 나레 없는 창도 원본 순서를 지켜야 해서 나레 밑 창을 밀어냈다(0:48~1:17 +7~28초)."""
    NA = [x for x in A if narrated(x)]; FR = [x for x in A if not narrated(x)]
    if NA: place(NA, fixed, lo, hi)
    done = list(fixed) + NA; lasthold = [None]
    for x in sorted(FR, key=lambda x: x["a"]):
        L = slen(x); t = src_at((x["a"] + x["b"]) / 2) - L / 2
        ok = (grid >= lo) & (grid + L <= hi)
        for w in done: ok &= ~((grid < w["s"] + slen(w) + GAP) & (grid + L + GAP > w["s"]))
        cost = np.abs(grid - t) / TW
        m = np.clip(((grid + L / 2) * 4).astype(int), 0, len(HQ) - 1); tm = min(int((t + L / 2) * 4), len(HQ) - 1)
        cost = cost + VW * (np.abs(HQ[m] - HQ[tm]).mean(1) + 0.5 * np.abs(CQ[m] - CQ[tm]).mean(1))
        i0 = np.minimum((grid / 0.05).astype(int), len(csum) - 1); i1 = np.minimum(((grid + L) / 0.05).astype(int), len(csum) - 1)
        cost = cost + np.where(csum[i1] - csum[i0] > 0.2, (8 + 6 * (csum[i1] - csum[i0])) / TW, 0)
        # 10-13 "3분쯤에 핀치가 대피하고 씻는 장면이 중간중간 나와": 가장 가까운 빈자리가 수십 초 뒤 장면(씻기)일 수 있었다
        # → 벤치 자리 기준 뒤로 BACK·앞으로 FWD 초 안(같은 장면)에서만. 없으면 앞 창 끝 그림 멈춤(holdprev → merge_hold)
        lo2 = max(t - BACK, scene_start(t + L / 2))     # 제브가 나눈 같은 장면(scenes_jev.json)의 지난 부분 ~ 벤치 자리 + FWD
        vd = np.abs(HQ[m] - HQ[tm]).mean(1)              # 벤치 그 순간 그림과 다른 정도(check_all ③ 잣대)
        # 10-13: 밝기 분포(vd)만으로는 주황 모래폭풍과 어두운 샤워실을 닮았다고 봤다 → 제브가 컷마다 고른 장소·핀치 차림(jev_attr_out.jsonl)이 벤치 그림과 맞아야
        pc = place_ok(t + L / 2)
        far = (grid > t + FWD) & (grid <= t + FWD2) & (GSC == scene_id(t + L / 2))                # 대화 장면 반응 컷: 같은 장면
        c1 = np.where(ok & pc & (((grid >= lo2) & (grid <= t + FWD)) | far), cost, 1e12); p = int(np.argmin(c1))
        if c1[p] >= 1e11:                                 # 마지막: 장면이 달라도 같은 장소·차림(제브) ±120초
            c1 = np.where(ok & pc & (np.abs(grid - t) <= 120), cost, 1e12); p = int(np.argmin(c1))
        if c1[p] >= 1e11 and L > 1.6:                     # 2초 넘게 멈추느니 같은 장소·차림 ±300초
            c1 = np.where(ok & pc & (np.abs(grid - t) <= 300), cost, 1e12); p = int(np.argmin(c1))
        if c1[p] >= 1e11 and L > 1.6:                     # 제브 장소 표가 어긋난 곳(은신처 부엌이 rv/other 로 갈림) — ±60초 차림만 맞으면
            i0 = min(int((t + L / 2) / ST), NP - 1); lk = (GLK == GLK[i0]) | (GLK[i0] == 0) | (GLK == 0)
            lk = np.where(grid > t + FWD, (GLK == GLK[i0]) & (GLK[i0] != 0), lk)      # 뒤 장면은 차림을 알고 같을 때만
            c1 = np.where(ok & lk & (np.abs(grid - t) <= 60), cost, 1e12); p = int(np.argmin(c1))
        if c1[p] >= 1e11 and lasthold[0] is not None and abs(lasthold[0] - x["a"]) < 0.01:   # 멈춤이 3초 넘게 이어지면 조건 없이 ±60초
            c1 = np.where(ok & (np.abs(grid - t) <= 60), cost, 1e12); p = int(np.argmin(c1))
        if c1[p] >= 1e11: x["s"] = -1.0; x["holdprev"] = True; lasthold[0] = x["b"]; continue
        x["s"] = round(p * ST, 3); done.append(x)
    return A
BACK, FWD = float(os.environ.get("BACK", 300)), float(os.environ.get("FWD", 8))
_SC = json.load(open("scenes_jev.json")) if os.path.exists("scenes_jev.json") else []
_S0 = {}
for _x in _SC: _S0.setdefault(_x["scene"], _x["s"])
def scene_start(t):
    if not _SC: return t - 25.0
    x = next((x for x in _SC if x["s"] <= t < x["e"]), _SC[-1]); return _S0[x["scene"]]
def scene_id(t):
    if not _SC: return -1
    return next((x for x in _SC if x["s"] <= t < x["e"]), _SC[-1])["scene"]
FWD2 = float(os.environ.get("FWD2", 90))
GSC = np.full(NP, -2)
for _x in _SC: GSC[int(_x["s"] / ST):int(_x["e"] / ST) + 1] = _x["scene"]
_PL = {"desert": 1, "city": 2, "vehicle_cab": 3, "rv": 4, "shelter": 5, "other_building": 6}
_LK = {"suit": 1, "shirtless": 2, "clothes": 3, "absent": 4}
GPL = np.zeros(NP, int); GLK = np.zeros(NP, int)
if os.path.exists("jev_attr_out.jsonl"):
    _AT = {int(json.loads(l)["id"][1:]): json.loads(l)["answers"] for l in open("jev_attr_out.jsonl", encoding="utf-8")}
    for _x in _SC:
        _a = _AT.get(_x["i"])
        if _a:
            GPL[int(_x["s"] / ST):int(_x["e"] / ST) + 1] = _PL.get(_a["place"]["choice"], 0)
            GLK[int(_x["s"] / ST):int(_x["e"] / ST) + 1] = _LK.get(_a["finch_look"]["choice"], 0)
def place_ok(t):
    """원본 자리마다 벤치 그림(t)과 장소가 같고 핀치 차림이 어긋나지 않나. 모르는 것(0)은 통과.
    ★단 벤치 자리보다 FWD 초 넘게 뒤(앞으로 나올 장면)는 차림을 «알고 같을 때만» — 3:33 샤워 컷(차림 모름)이 보호복 장면에 끼던 것."""
    i = min(int(t / ST), NP - 1); p0, l0 = GPL[i], GLK[i]
    okp = (GPL == p0) | (p0 == 0) | (GPL == 0)
    okl = (GLK == l0) | (l0 == 0) | (GLK == 0)
    fut = grid > t + FWD
    okl = np.where(fut, (GLK == l0) & (l0 != 0), okl)
    return okp & okl
def merge_hold(ws):
    out = []
    for w in sorted(ws, key=lambda w: w["a"]):
        if w.get("holdprev") and out:
            p = out[-1]
            if p["kind"] == "D" and "sub1" not in p: p["sub1"] = round(p["b"] - p["a"] - 0.05, 3)
            p["hold"] = round(p.get("hold", 0) + (w["b"] - w["a"]), 3); p["b"] = w["b"]
        else: out.append(w)
    return out

def split(t0, t1):
    out = []; t = t0
    while t1 - t > 0.05:
        L = min(MAXC, t1 - t)
        if t1 - t - L < 0.8 and t1 - t > MAXC: L = (t1 - t) / 2
        out.append({"a": round(t, 3), "b": round(t + L, 3), "kind": "A"}); t += L
    return out

# ── 훅 0 ~ 84.65
HEND = 84.65
assert any(abs(w["a"] - HEND) < 0.02 for w in WN)
HD = [{"a": 16.15, "b": 19.25, "s": 2254.15, "kind": "D", "ko": "제발, 맙소사 / 주의, 심장 박동 상승"},
      {"a": 23.55, "b": 26.65, "s": 2261.55, "kind": "D", "ko": "캠핑카로 돌아가야 해요"},
      {"a": 32.27, "b": 34.0, "s": 2276.0, "kind": "D", "ko": "274m"},            # 벤치 0:32.3 (900. 2276.01~2276.67)
      {"a": 55.8, "b": 57.5, "s": 2319.85, "kind": "D", "ko": "뭐든 꽉 잡아"},
      {"a": 59.5, "b": 63.05, "s": 2334.0, "kind": "D", "ko": "15m, 최대한 주의"}]
HA = []; t = 0.0
for d in HD + [{"a": HEND, "b": HEND}]:
    HA += split(t, d["a"]); t = d["b"]
place2(HA, HD)
hook = sorted(HA + HD, key=lambda w: w["a"])

# ── 본편 첫 창들 84.65 ~ (N10 끝 1:35.7 뒤 첫 대사 창 전까지)
rest = [w for w in WN if w["a"] >= HEND - 0.01]
k = next(i for i, w in enumerate(rest) if w["a"] > 96 and w["kind"] == "D")      # 1:45.9 「내가 죽을 날이라고…」 앞까지
MA = [dict(w) for w in rest[:k] if w["kind"] == "A"]; MD = [w for w in rest[:k] if w["kind"] == "D"]
for x in MA: x.pop("s", None)
place2(MA, MD + rest[k:], lo=62.0)
main0 = sorted(MA + MD, key=lambda w: w["a"])
WN = merge_hold(hook + main0 + rest[k:]); assert all(w["s"] >= 0 for w in WN)

# 검사
for i in range(len(WN) - 1): assert abs(WN[i]["b"] - WN[i + 1]["a"]) < 0.005, (i, WN[i], WN[i + 1])
def zone(t): return "hook" if t < ZB else "crit" if t >= 1592 else "main"
for z in ("hook", "main", "crit"):
    sp = sorted((w["s"], w["s"] + slen(w)) for w in WN if zone(w["a"]) == z)
    bad = [(round(sp[i][1], 2), round(sp[i + 1][0], 2)) for i in range(len(sp) - 1) if sp[i + 1][0] - sp[i][1] < GAP - 0.01]
    assert not bad, (z, bad)
assert not [w for w in WN if w["kind"] == "D" and any(w["a"] + 0.05 < y - 0.25 and w["b"] - w.get("hold", 0) - 0.05 > x + 0.25 for x, y in NAR)]   # hold 부분은 소리 없음
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
print("훅·첫 창: 벤치 자리와 차이(초)")
for w in [w for w in WN if w["a"] < 96]:
    want = src_at((w["a"] + w["b"]) / 2); got = w["s"] + slen(w) / 2
    print(f"  {mm(w['a'])} {w['kind']}{'N' if narrated(w) else '-'} 원본 {w['s']:.1f}  벤치 {want - slen(w) / 2:.1f}  차이 {got - want:+.1f} {w.get('ko', '')}")
json.dump(WN, open("windows_v8.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("훅 멈춤", round(sum(w.get("hold", 0) for w in WN if w["a"] < 96), 1), "초")

if os.environ.get("DRY"): sys.exit()   # 시험: 창만 쓰고 캐시는 안 건드림
# 캐시 옮기기 (fix4 와 같음)
def key(w): return (round(w["a"], 3), round(w["b"], 3), round(w["s"], 3), w["kind"], w.get("hold", 0))
CUR = json.load(open("clips_v8_index.json", encoding="utf-8"))
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
json.dump(WN, open("clips_v8_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("창", len(CUR), "→", len(WN), "· 캐시 그대로", kept, "· 새로 자를 것", len(WN) - kept)
