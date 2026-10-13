# -*- coding: utf-8 -*-
"""v8 열째 손질 (10-13, "중간에 영상이잠깐씩 멈추는것도 보이던데" 같은 원인 더 찾기) — 멈춤(hold)을 없앤 뒤 완성본을 blackdetect 로 재 보니
원본이 까만 화면(정전·장면 전환 암전)인 창이 벤치는 그림이 있는 자리에서 0.75~3초 까맣게 나왔다(5:19 「그럴 가치가 있을 거야」·6:46 「젠장」 등).
화면이 까맣게 서 있으면 멈춘 것처럼 보인다.
판정: fp_src.npy(원본 0.25초마다 그림 지문)의 밝기 90% 값 < 0.07 = 까만 그림. 창의 원본 구간 까만 초 ≥ 0.75 이고 벤치가 그 순간 쓴 원본보다 0.5초 넘게 많으면 고침.
 - 액션 창: 같은 장면·장소·차림(제브) 빈자리 중 까만 그림이 0.25초 안인 곳, 벤치 자리에 가장 가까운 곳으로 옮김(3초 간격 지킴)
 - 대사 창: 말소리·자막은 그대로 두고 그림만 같은 장면 빈자리에서(vs = 그림 원본 시작, build_v8 cut() 지원)
사용: python fix10_v8.py → windows_v8.json (옛 것 windows_v8_pre10.json), 캐시 clips_v8_index.json"""
import json, os, shutil, sys, numpy as np
SPD, GAP, TH = 1.05, 3.0, 0.07
W = json.load(open("windows_v8.json", encoding="utf-8"))
if not os.path.exists("windows_v8_pre10.json"): shutil.copy("windows_v8.json", "windows_v8_pre10.json")
E = json.load(open("edl.json")); SC = json.load(open("scenes_jev.json"))
AT = {int(json.loads(l)["id"][1:]): json.loads(l)["answers"] for l in open("jev_attr_out.jsonl", encoding="utf-8")}
FA = np.load("fp_src.npy"); P90 = np.percentile(FA.reshape(len(FA), -1).astype(np.float32) / 255, 90, axis=1); del FA
DARK = P90 < TH
def rate(w): return w.get("rate", SPD) if w["kind"] == "A" else 1.0
def slen(w): return (w["b"] - w["a"] - w.get("hold", 0)) * rate(w)
def zone(t): return "hook" if t < 84.6 else "crit" if t >= 1592 else "main"
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
def src_at(t):
    g = next((g for g in E if g["b0"] <= t < g["b1"]), E[-1]); return g["s0"] + (t - g["b0"])
def dark_sec(s, L): return DARK[max(0, int(s * 4)):max(0, int((s + L) * 4))].sum() / 4
def cut_of(t): return next((x for x in SC if x["s"] <= t < x["e"]), SC[-1])
def attr(t):
    a = AT.get(cut_of(t)["i"]); return (a["place"]["choice"], a["finch_look"]["choice"]) if a else (None, None)
def spans(z, skip=None):
    out = []
    for j, x in enumerate(W):
        if j == skip or zone(x["a"]) != z: continue
        out.append((x["s"], x["s"] + slen(x)))
        if "vs" in x: out.append((x["vs"], x["vs"] + slen(x)))
    return sorted(out)
def pick(k, L, own=None):
    """창 k 의 그림 자리: 벤치 그 순간과 같은 장면(−60~+90초, 없으면 같은 장소·차림 ±120초), 까만 그림 0.25초 안, 3초 간격"""
    w = W[k]; z = zone(w["a"]); bt = src_at((w["a"] + w["b"]) / 2) - L / 2
    bp, bl = attr(bt + L / 2); bsc = cut_of(bt + L / 2)["scene"]
    sp = spans(z, k)
    if own: sp = sorted(sp + [own])                          # 대사 창 말소리 구간도 피함
    def ok_look(m):
        cp, cl = attr(m); return cp == bp and (cl == bl or "absent" in (cl, bl) or "none" in (cl, bl))
    for tier in (0, 1, 2):
        best = None
        for c in np.arange(max(0.0, bt - 150), bt + 150, 0.25):
            if any(c < q1 + GAP and c + L + GAP > q0 for q0, q1 in sp): continue
            m = c + L / 2
            if tier == 0 and not (-60 <= c - bt <= 90 and cut_of(m)["scene"] == bsc and ok_look(m)): continue
            if tier == 1 and not (abs(c - bt) <= 120 and ok_look(m)): continue
            if tier == 2 and not (abs(c - bt) <= 60 and cut_of(m)["scene"] == bsc): continue      # 같은 장면이면 장소 표가 갈려도(차 밖↔차 안)
            if dark_sec(c, L) > 0.25: continue
            if best is None or abs(c - bt) < abs(best - bt): best = float(c)
        if best is not None: return best, tier
    return None, None
fixed = 0
for k, w in enumerate(W):
    L = slen(w); s0 = w.get("vs", w["s"]); blk = dark_sec(s0, L)
    bb = dark_sec(src_at(w["a"]), (w["b"] - w["a"]) * rate(w))
    if blk < 0.75 or blk - bb < 0.5: continue
    if w["kind"] == "A":
        c, tier = pick(k, L)
        if c is None: print(f"  {k} {mm(w['a'])} A 까만 {blk:.2f}초 — 옮길 자리 없음"); continue
        print(f"  {k} {mm(w['a'])} A 까만 {blk:.2f}초(벤치 {bb:.2f}) 원본 {w['s']:.1f} → {c:.1f} {('같은 장면', '같은 장소·차림', '같은 장면(장소 표 다름)')[tier]} {attr(c + L / 2)}")
        w["s"] = round(c, 3)
    else:
        c, tier = pick(k, L, (w["s"], w["s"] + L))
        if c is None: print(f"  {k} {mm(w['a'])} D 까만 {blk:.2f}초 — 그림 자리 없음"); continue
        print(f"  {k} {mm(w['a'])} D 「{w.get('ko', '')}」 까만 {blk:.2f}초(벤치 {bb:.2f}) 그림만 원본 {c:.1f} {('같은 장면', '같은 장소·차림', '같은 장면(장소 표 다름)')[tier]} {attr(c + L / 2)}")
        w["vs"] = round(c, 3)
    fixed += 1
print("고친 창", fixed)
for z in ("hook", "main", "crit"):
    sp = spans(z)
    bad = [(round(sp[i][1], 2), round(sp[i + 1][0], 2)) for i in range(len(sp) - 1) if sp[i + 1][0] - sp[i][1] < GAP - 0.01]
    assert not bad, (z, bad)
if os.environ.get("DRY"): sys.exit()
json.dump(W, open("windows_v8.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
def key(w): return (round(w["a"], 3), round(w["b"], 3), round(w["s"], 3), w["kind"], w.get("hold", 0), w.get("rate", 0), w.get("vs", -1))
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
print("창", len(W), "· 캐시 그대로", kept, "· 새로 자를 것", len(W) - kept)
