# -*- coding: utf-8 -*-
"""v8 아홉째 손질 (10-13 "중간에 영상이잠깐씩 멈추는것도 보이던데 왜그래?") — 멈춤(hold: 앞 창 끝 그림을 멈춰 세움) 18곳 23.9초를 모두 실제 영상으로.
fix4(0.2초 깜빡 컷)·fix5/6(같은 장면·장소·차림 빈자리가 없을 때)가 넣은 hold 는 화면이 1~3초 얼어붙어 보였다.
창 k 끝의 멈춤 H 초를 이 순서로 메운다(원본 3초 간격은 그대로, 대사 말·자막 시각은 그대로):
 a) k 를 원본에서 더 틀기(뒤로) — 3초 간격 여유만큼, 대사 창·나레 없는 액션 창은 다음 말소리 전까지
 b) k 가 액션 창이면 원본 앞쪽으로도 더 틀기
 c) 다음 창 k+1 을 앞당기기(출력 시작과 원본 시작을 같이 당김 → 말 싱크 그대로, 대사 창이면 sub0/sub1 도 같이 밀어 자막 시각 고정)
 d) 그래도 남으면: k 가 액션 창이면 k 가 든 액션 창 묶음, 대사 창이면 뒤 액션 창 묶음(사이 대사 창은 나레와 안 겹칠 때 통째로 당김)을
    고르게 조금 느리게(rate, 기본 1.05 → 0.8 이상). 멈춘 그림 대신 천천히 움직이는 그림.
사용: python fix9_v8.py → windows_v8.json (옛 것 windows_v8_pre9.json), 캐시 clips_v8_index.json"""
import json, os, shutil, sys
SPD, GAP, MINR = 1.05, 3.0, 0.8
W = json.load(open("windows_v8.json", encoding="utf-8"))
if not os.path.exists("windows_v8_pre9.json"): shutil.copy("windows_v8.json", "windows_v8_pre9.json")
SW = json.load(open("src_words.json", encoding="utf-8")); PL = json.load(open("narr_place.json"))
NAR = [(q["t"], q["t"] + q["d"]) for q in PL]
def rate(w): return w.get("rate", SPD) if w["kind"] == "A" else 1.0
def slen(w): return (w["b"] - w["a"] - w.get("hold", 0)) * rate(w)
def zone(t): return "hook" if t < 84.6 else "crit" if t >= 1592 else "main"
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
def nov(a, b): return sum(max(0, min(b, y) - max(a, x)) for x, y in NAR)
def talky(w): return w["kind"] == "D" or nov(w["a"], w["b"]) < 0.3        # 원본 소리가 들리는 창 → 말소리 피함
def others(k):
    z = zone(W[k]["a"]); return [(x["s"], x["s"] + slen(x)) for j, x in enumerate(W) if j != k and zone(x["a"]) == z]
def room_end(k):
    s1 = W[k]["s"] + slen(W[k]); r = min([o[0] - GAP - s1 for o in others(k) if o[0] >= s1 - 0.01] + [99])
    if talky(W[k]):                                                       # 다음 말소리(이 창 말 꼬리는 빼고) 0.1초 전까지
        nx = [x[0] for x in SW if x[0] >= s1 + 0.02]
        if nx: r = min(r, min(nx) - 0.1 - s1)
    return max(0.0, r)
def room_st(k):
    s0 = W[k]["s"]; r = min([s0 - o[1] - GAP for o in others(k) if o[1] <= s0 + 0.01] + [99])
    if talky(W[k]):
        pv = [x[1] for x in SW if x[1] <= s0 - 0.02]
        if pv: r = min(r, s0 - 0.1 - max(pv))
    return max(0.0, r)
def sub_shift(w, y):            # 대사 창 시작을 y 초 당겼을 때 자막 절대 시각을 그대로
    w["sub0"] = round(w.get("sub0", 0.05) + y, 3); w["sub1"] = round(w.get("sub1", w["b"] - w["a"] - 0.05) + y, 3)
def spread(i0, i1, extra_front=0.0):
    """W[i0..i1] 액션 창 묶음을 고르게 느리게. 묶음 끝은 고정, 시작은 extra_front 초 앞당김. 반환: 새 rate"""
    a0 = W[i0]["a"] - extra_front; b1 = W[i1]["b"]
    src = sum(slen(W[i]) for i in range(i0, i1 + 1)); r = src / (b1 - a0)
    t = a0
    for i in range(i0, i1 + 1):
        L = slen(W[i]) / r; W[i]["a"] = round(t, 3); t += L; W[i]["b"] = round(t, 3); W[i]["rate"] = round(r, 4); W[i]["hold"] = 0
        if i == i1: W[i]["b"] = round(b1, 3)
    return r
# e) 끼워 넣기용: 같은 장면·장소·차림(제브 scenes_jev.json · jev_attr_out.jsonl) 빈자리
E = json.load(open("edl.json")); SC = json.load(open("scenes_jev.json"))
AT = {int(json.loads(l)["id"][1:]): json.loads(l)["answers"] for l in open("jev_attr_out.jsonl", encoding="utf-8")}
def src_at(t):
    g = next((g for g in E if g["b0"] <= t < g["b1"]), E[-1]); return g["s0"] + (t - g["b0"])
def cut_of(t): return next((x for x in SC if x["s"] <= t < x["e"]), SC[-1])
def attr(t):
    a = AT.get(cut_of(t)["i"]); return (a["place"]["choice"], a["finch_look"]["choice"]) if a else (None, None)
def free_slot(k, L, t0, t1, speech_ok=False):
    """출력 [t0,t1] 에 끼울 원본 시작. 벤치 그 순간과 같은 장면(−60~+90초)·같은 장소·차림이 어긋나지 않는 곳, 3초 간격, 말소리 피함"""
    z = zone(t0); bt = src_at((t0 + t1) / 2); bp, bl = attr(bt); bsc = cut_of(bt)["scene"]
    sp = sorted((x["s"], x["s"] + slen(x)) for x in W if zone(x["a"]) == z)
    talk = nov(t0, t1) < 0.3; best = None
    for (p0, p1), (q0, q1) in zip(sp, sp[1:]):
        lo, hi = p1 + GAP, q0 - GAP - L
        if hi < lo: continue
        c = min(max(bt - L / 2, lo), hi)
        if not (-60 <= c - bt <= 90): continue
        m = c + L / 2; cp, cl = attr(m)
        if cut_of(m)["scene"] != bsc or cp != bp or (cl != bl and "absent" not in (cl, bl) and "none" not in (cl, bl)): continue
        if talk and not speech_ok and any(x[0] < c + L and x[1] > c for x in SW): continue      # 말소리 있으면 build 가 0.3 으로 낮춤
        if best is None or abs(c - bt) < abs(best - bt): best = c
    return best
def plan_slow(k, R):
    """멈춤 R 을 느리게 틀어 메울 때의 (i0, i1, 앞당김, 당길 대사 창들, rate) — 적용 안 함"""
    w = W[k]; z = zone(w["a"])
    if w["kind"] == "A":
        i0, i1 = k, k
        while i0 - 1 >= 0 and W[i0 - 1]["kind"] == "A" and zone(W[i0 - 1]["a"]) == z and k - i0 < 3: i0 -= 1
        while i1 + 1 < len(W) and W[i1 + 1]["kind"] == "A" and zone(W[i1 + 1]["a"]) == z and i1 - k < 3: i1 += 1
        src = sum(slen(W[i]) for i in range(i0, i1 + 1)); return i0, i1, 0.0, [], src / (W[i1]["b"] - W[i0]["a"])
    j = k + 1
    while W[j]["kind"] == "D":
        if nov(W[j]["a"] - R, W[j]["b"] - R) > nov(W[j]["a"], W[j]["b"]) + 0.1: return None
        j += 1
    i1 = j
    while i1 + 1 < len(W) and W[i1 + 1]["kind"] == "A" and zone(W[i1 + 1]["a"]) == z and i1 - j < 3: i1 += 1
    src = sum(slen(W[i]) for i in range(j, i1 + 1)); return j, i1, R, list(range(k + 1, j)), src / (W[i1]["b"] - W[j]["a"] + R)
targets = [w for w in W if w.get("hold", 0) > 0]
print("멈춤", len(targets), "곳 · 합", round(sum(w["hold"] for w in targets), 2), "초")
for w in targets:
    k = next(i for i, x in enumerate(W) if x is w); H = w.get("hold", 0)
    if H <= 0: continue
    msg = [f"{k} {mm(w['a'])} {w['kind']} 멈춤 {H:.2f}"]
    x = min(H, room_end(k) / rate(w)); w["hold"] = round(w["hold"] - x, 3); msg.append(f"a 뒤로 {x:.2f}")
    if w["kind"] == "A" and w["hold"] > 0.01:
        x = min(w["hold"], room_st(k) / rate(w)); w["s"] = round(w["s"] - x * rate(w), 3); w["hold"] = round(w["hold"] - x, 3); msg.append(f"b 앞으로 {x:.2f}")
    n = W[k + 1]
    if w["hold"] > 0.01 and zone(n["a"]) == zone(w["a"]):
        y = min(w["hold"], room_st(k + 1) / rate(n))
        if y > 0.005:
            if n["kind"] == "D": sub_shift(n, y)
            w["b"] = round(w["b"] - y, 3); w["hold"] = round(w["hold"] - y, 3)
            n["a"] = round(n["a"] - y, 3); n["s"] = round(n["s"] - y * rate(n), 3)
            msg.append(f"c 다음 창 당김 {y:.2f}")
    R = w["hold"]
    if R > 0.01:
        pl = plan_slow(k, R); c = None
        if (pl is None or pl[4] < 0.88) and R >= 0.8:
            c = free_slot(k, R * SPD, w["b"] - R, w["b"])
            if c is None: c = free_slot(k, R * SPD, w["b"] - R, w["b"], True)
        if c is not None:                                   # e) 같은 장면 빈자리 컷을 끼워 넣음
            W.insert(k + 1, {"a": round(w["b"] - R, 3), "b": w["b"], "kind": "A", "s": round(c, 3), "ins": 1})
            w["b"] = round(w["b"] - R, 3); w["hold"] = 0
            msg.append(f"e 끼움 원본 {c:.1f} (벤치 {src_at(W[k + 1]['a']):.1f}) {attr(c + R * SPD / 2)}")
        elif pl is not None and pl[4] >= MINR:              # d) 느리게
            i0, i1, front, ds, _ = pl
            if w["kind"] == "D":
                w["b"] = round(w["b"] - R, 3); w["hold"] = 0
                for m in ds: W[m]["a"] = round(W[m]["a"] - R, 3); W[m]["b"] = round(W[m]["b"] - R, 3)
            r = spread(i0, i1, front); msg.append(f"d {'대사 ' + str(len(ds)) + '개 당기고 ' if ds else ''}액션 {i0}~{i1} 느리게 ×{r:.2f}")
        else: msg.append(f"못 메움 (느리게 ×{pl[4]:.2f})" if pl else "못 메움(나레와 겹침)")
    print("  " + " · ".join(msg))
left = [(k, w["hold"]) for k, w in enumerate(W) if w.get("hold", 0) > 0.005]
for w in W:
    if w.get("hold", 1) <= 0.005: w.pop("hold", None)
rs = [w["rate"] for w in W if "rate" in w]
print("남은 멈춤", left, "· 느리게 튼 창", len(rs), "· 가장 느림", min(rs) if rs else None)
for i in range(len(W) - 1): assert abs(W[i]["b"] - W[i + 1]["a"]) < 0.005, (i, W[i], W[i + 1])
for w in W:
    assert w["b"] - w["a"] > 0.25, w
    if w["kind"] == "D": assert w.get("sub1", w["b"] - w["a"] - 0.05) <= w["b"] - w["a"] + 0.01 and w.get("sub0", 0.05) >= 0, w
assert not rs or min(rs) >= MINR, min(rs)
for z in ("hook", "main", "crit"):
    sp = sorted((w["s"], w["s"] + slen(w)) for w in W if zone(w["a"]) == z)
    bad = [(round(sp[i][1], 2), round(sp[i + 1][0], 2)) for i in range(len(sp) - 1) if sp[i + 1][0] - sp[i][1] < GAP - 0.01]
    assert not bad, (z, bad)
if os.environ.get("DRY"): sys.exit()
json.dump(W, open("windows_v8.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
def key(w): return (round(w["a"], 3), round(w["b"], 3), round(w["s"], 3), w["kind"], w.get("hold", 0), w.get("rate", 0))
CUR = json.load(open("clips_v8_index.json", encoding="utf-8"))
oldk = {key(w): i for i, w in enumerate(CUR)}
os.makedirs("clips_v8/_old", exist_ok=True)
for f in os.listdir("clips_v8"):
    if f.endswith(".mkv"): shutil.move(f"clips_v8/{f}", f"clips_v8/_old/{f}")
kept = 0
for j, w in enumerate(W):
    o = oldk.get(key(w))
    if o is not None and os.path.exists(f"clips_v8/_old/c{o:04d}.mkv"):
        shutil.move(f"clips_v8/_old/c{o:04d}.mkv", f"clips_v8/c{j:04d}.mkv"); kept += 1
shutil.rmtree("clips_v8/_old")
json.dump(W, open("clips_v8_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("창", len(CUR), "→", len(W), "· 캐시 그대로", kept, "· 새로 자를 것", len(W) - kept)
