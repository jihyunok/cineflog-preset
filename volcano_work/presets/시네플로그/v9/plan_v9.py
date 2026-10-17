# -*- coding: utf-8 -*-
"""시네플로그 v9 창 짜기 — 대본(script.py)의 줄마다 그 줄이 말하는 원본 장면 구간 안에서만 3초 조각을 순서대로 고른다.
10-13 밤 사용자(17 그레이하운드):
 "나래이션과 나래이션이 말하는 영상이 맞아야해 그건 가장 기본이야 핀치가 방으로 들어옵니다 들어오는 영상이 붙어야되는게 맞는거지?"
 "벤치의 흐름대로 가져가는거야 똑같이 하지마"
 "3초쓰고 다른 3초영상 말이되게 어색하지않는 상황으로 붙이면되 ... 영상을 다 잘라 잘라서 말이되게 이어붙이고 나래이션 넣어"
 "핀치하나 만드는데 3일걸렸어" → 처음부터 한 번에: 멈춤(hold) 없음 · 깜빡 컷 없음 · 대사 가장자리는 말소리에(v9/edges.py) · 3초 간격은 계획에서 보장 · 못 채우면 그 줄을 찍고 실패(몰래 메우지 않음).

대본 꼴 (작업 폴더 script.py 의 S 목록, 위에서부터 화면 순서):
  ("ZONE", "hook"|"main"|"outro")              3초 간격은 구역 안에서(훅·아웃트로는 예고편처럼 본편 장면을 다시 쓰는 자리)
  ("N", "나레 문장", 원본a, 원본b)              나레 + 그 밑 그림은 원본 [a,b] 안에서만(그 문장이 말하는 장면). 조각마다 2.9초 안·좌우반전·1.05배속
  ("N", "나레 문장", [(a1,b1), (a2,b2)…])       문장 속 동작이 여럿이면 조각마다 구간을 따로(「구두끈을 매고 → 모자를 씁니다」) — 조각 수 = 구간 수
  ("D", 줄id 또는 [줄id…], "우리 자막")        원본 대사(lines.json, Speechmatics 시각) — 말소리 가장자리에 맞춤, ★화면 3초 안(1.05배속 — 영상·소리 같이), 반전
      ★10-14 17 그레이하운드 v10 도 Apple IPE 소유권 주장 그대로(대사 창 최장 5.9초·63%) → 사용자 "1"(대사 창 3초 이하)·"나래이션으로 바꿔줘":
      대사 창은 처음부터 1.05배(rate)로 짜고 말소리 3.15초(화면 3.0초)를 넘으면 실패 — 넘는 대사는 나레로 바꾸거나 두 사람 말 중 한쪽만. drate.py 는 이제 안 돌린다.
  ("A", 원본a, 원본b, 화면초)                   나레·자막 없이 원본 소리(폭발·함성 등) 조각. 화면초 만큼 [a,b] 안에서
나레 길이: narr/nNNN.wav 가 있으면 그 길이, 없으면 띄어쓰기 뺀 글자 수 ÷ 6.5자/초(제미나이 Ludo 실측)로 어림(--dry).
사용: python plan_v9.py [--dry] → windows.json · narr_place.json · plan_report.txt (실패 줄이 있으면 exit 1)"""
import json, math, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edges as EDG
CFG = json.load(open("ep.json", encoding="utf-8"))
SRC, SRCLEN = CFG["src"], CFG["srclen"]
SPD, GAP, MAXC = 1.05, 3.0, 2.9
DMAX, DSPD = CFG.get("dmax", 3.0), CFG.get("dspd", 1.05)     # 대사 창 화면 최장(초)·배속 (10-14 CID)
CPS = 6.5          # 제미나이 Ludo 실측(16 핀치 148조각): 띄어쓰기 뺀 글자 6.51자/초
DRY = "--dry" in sys.argv
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
cuts = np.array(sorted(float(x) for x in re.findall(r"(?:pts_time:)?(\d+\.\d+)", open(CFG.get("scenes", "scenes.txt")).read())))
# 까만 화면: black_src.npy(black_map.py — 색 채널 최대값 98% < 0.08). 회색 지문 밝기만 보면 붉은 조명 함교를 까맣다고 본다(17 그레이하운드)
if os.path.exists("black_src.npy"): DARK = np.load("black_src.npy") < 0.08
else:
    FA = np.load("fp_src.npy").astype(np.float32); DARK = np.percentile(FA.reshape(len(FA), -1) / 255, 90, axis=1) < 0.07; del FA
env = EDG.Env(SRC, CFG.get("words", "src_words.json"), cache=CFG.get("band", "src_band.npy"))
SPEECH = np.zeros(int(SRCLEN / 0.05) + 10)
for w in env.W: SPEECH[int(w[0] / 0.05):int(w[1] / 0.05) + 1] = 1
CS = np.concatenate([[0], np.cumsum(SPEECH)]) * 0.05
def speech(a, b): return CS[min(len(CS) - 1, int(b / 0.05))] - CS[min(len(CS) - 1, int(a / 0.05))]
def dark(a, b): return DARK[max(0, int(a * 4)):max(0, int(b * 4)) + 1].sum() / 4
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
def dur(p):
    import subprocess
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

# ── 1. 줄 → 화면 시간
items = []; zone = "main"; ni = 0; problems = []
for k, x in enumerate(S):
    if x[0] == "ZONE": zone = x[1]; continue
    opt = x[-1] if isinstance(x[-1], dict) else {}
    if opt: x = x[:-1]
    it = {"k": k, "kind": x[0], "zone": zone, "opt": opt}
    if x[0] == "N":
        ni += 1; it.update(ni=ni, text=x[1])
        if isinstance(x[2], (list, tuple)): it.update(parts=[(float(a), float(b)) for a, b in x[2]], a=float(x[2][0][0]), b=float(x[2][-1][1]))
        else: it.update(a=float(x[2]), b=float(x[3]))
        w = f"narr/n{ni:03d}.wav"
        same = os.path.exists(w) and json.load(open(w[:-4] + ".json", encoding="utf-8")).get("text") == x[1]   # --dry 도 글이 같은 녹음은 실제 길이(10-14 줄 바꾼 뒤 번호 다시 매김)
        it["d"] = dur(w) if same or (os.path.exists(w) and not DRY) else len(re.sub(r"\s", "", x[1])) / CPS
        if not DRY and os.path.exists(w) and not same: problems.append(f"줄{k} 나레 n{ni:03d}.wav 글이 대본과 다름")
        if not DRY and not os.path.exists(w): problems.append(f"줄{k} 나레 n{ni:03d}.wav 없음")
    elif x[0] == "D":
        ids = x[1] if isinstance(x[1], list) else [x[1]]
        ln = [L[i] for i in ids]
        s0 = min(l["ws"] for l in ln if l["ws"] is not None); e0 = max(l["we"] for l in ln if l["we"] is not None)
        s2, e2, note = env.snap(s0, e0, DMAX * DSPD)
        it.update(ids=ids, ko=x[2], s=s2, e=e2, d=(e2 - s2) / DSPD, sl=e2 - s2, note=note, en=" / ".join(l["en"] for l in ln))
        if e2 - s2 > DMAX * DSPD + 1e-6: problems.append(f"줄{k} 대사 {ids} 가 화면 {(e2 - s2) / DSPD:.2f}초 — {DMAX}초 넘음(나레로 바꾸거나 한쪽 말만)")
        for side, t in (("시작", s2), ("끝", e2)):
            why = env.edge_bad(t, "s" if side == "시작" else "e", s2, e2)
            if why: problems.append(f"줄{k} 대사 {ids} {side} {mm(t)} 말 잘림: {why}")
    elif x[0] == "A":
        it.update(a=float(x[1]), b=float(x[2]), d=float(x[3]))
    items.append(it)
# 대사 창은 말 끝에서 딱 끊는다(여백을 대사 창에 붙이면 그만큼 원본이 더 흘러 다음 사람 첫 낱말이 들어간다 — 17 관문 ⑦ 12곳).
# 대사 뒤 나레는 그림을 먼저 깔고 0.15초 뒤에 말을 시작(lead).
PAD = {("N", "N"): 0.25, ("N", "D"): 0.12, ("N", "A"): 0.1, ("A", "N"): 0.1, ("A", "D"): 0.1, ("A", "A"): 0.0}
t = 0.0
for i, it in enumerate(items):
    it["t"] = round(t, 3)
    prv = items[i - 1]["kind"] if i else "A"; nxt = items[i + 1]["kind"] if i + 1 < len(items) else "A"
    it["lead"] = 0.15 if (prv == "D" and it["kind"] == "N") else 0.0
    it["T"] = round(t + it["lead"] + it["d"] + PAD.get((it["kind"], nxt), 0.0), 3)       # 이 줄 그림이 차지하는 화면 끝(다음 줄 시작)
    t = it["T"]
BODY = t

# ── 2. 대사 창(고정) → 구역별 원본 사용 구간
used = {"hook": [], "main": [], "outro": []}
W = []
for it in items:
    if it["kind"] != "D": continue
    w = {"a": it["t"], "b": it["T"], "s": round(it["s"], 3), "kind": "D", "k": it["k"], "ko": it["ko"], "sub1": round(it["sl"], 3), "z": it["zone"]}
    w.update(it["opt"])                                            # 10-14 대사 창도 {"noflip": True} (뉴스 화면·모니터 글자 — 01 헤즈 오브 스테이트)
    if DSPD != 1: w["rate"] = DSPD                                 # build cut: 영상 setpts + 소리 atempo 같이 · 자막 시각은 원본 기준(build 가 /rate)
    parts = [p.strip() for p in it["ko"].split(" / ")]
    if len(parts) > 1 and len(parts) == len(it["ids"]):
        st = [max(0.05, L[i]["ws"] - it["s"]) for i in it["ids"]] + [it["sl"]]          # 원본 기준 초(build 가 /rate)
        w["subs"] = [[parts[j], round(st[j] if j else 0.05, 3), round(st[j + 1], 3)] for j in range(len(parts))]
    W.append(w); used[it["zone"]].append((it["s"], it["s"] + (it["T"] - it["t"]) * DSPD))
for z in used:
    sp = sorted(used[z])
    for x, y in zip(sp, sp[1:]):
        if y[0] - x[1] < GAP - 0.01: problems.append(f"{z} 대사끼리 원본 3초 간격 어김 {mm(x[0])}~{mm(x[1])} / {mm(y[0])}")

# ── 3. 나레·액션 줄: [a,b] 안에서 순서대로 조각 고르기 (DP, 0.1초 칸)
ST = 0.1
def free_mask(z, grid, sl):
    ok = np.ones(len(grid), bool)
    for x, y in used[z]: ok &= ~((grid < y + GAP) & (grid + sl + GAP > x))
    return ok
def shot_snap(p, sl, lo, hi):
    """조각 시작이 컷 시작 바로 뒤(0.6초 안)면 그 컷 시작으로 당긴다 — 다음 컷으로 밀면 다른 그림이 된다(10-13 「레이더에 표적이」 밑에 뱃머리)"""
    c = cuts[(cuts <= p) & (cuts > p - 0.6)]
    if len(c) and c[-1] + 0.06 >= lo: return float(c[-1]) + 0.06
    return p
def place_parts(it, d, z):
    """조각별 구간(parts) — 구간 j 안에서 조각 j, 원본 3초 간격"""
    P = it["parts"]; n = len(P); Lw = d / n; sl = Lw * SPD
    if Lw > MAXC + 1e-6: problems.append(f"줄{it['k']} 「{it.get('text', '')[:24]}」 조각 {n}개로는 {Lw:.1f}초씩 — 2.9초 넘음(구간을 늘리거나 나레를 줄일 것)"); return None
    ps = []
    for j, (lo, hi) in enumerate(P):          # 구간 순서가 원본 순서가 아니어도 된다(아웃트로) — 앞서 고른 조각·다른 줄 모두와 3초 간격
        mine = [(q, q + sl) for q in ps]
        c = [g for g in np.arange(lo, hi - sl + 1e-6, ST) if all(not (g < y + GAP and g + sl + GAP > x) for x, y in used[z] + mine)]
        if not c: problems.append(f"줄{it['k']} 「{it.get('text', '')[:24]}」 조각{j + 1} [{mm(lo)}~{mm(hi)}] 에 {sl:.1f}초 자리 없음"); return None
        g = min(c, key=lambda g: 2.0 * dark(g, g + sl) + abs(g - lo) * 0.05); ps.append(float(g))
    return ps, n, Lw, sl
for it in items:
    if it["kind"] == "D": continue
    d = it["T"] - it["t"]; n = max(1, math.ceil(d / MAXC - 1e-6)); Lw = d / n; sl = Lw * SPD
    lo, hi = it["a"], it["b"]; z = it["zone"]
    if it.get("parts"):
        r = place_parts(it, d, z)
        if r is None: continue
        ps, n, Lw, sl = r
        for j in range(n):
            a = it["t"] + Lw * j; b = it["t"] + Lw * (j + 1)
            W.append(dict({"a": round(a, 3), "b": round(b, 3), "s": round(ps[j], 3), "kind": "A", "k": it["k"], "z": z}, **it["opt"])); used[z].append((ps[j], ps[j] + sl))
        continue
    grid = np.arange(lo, max(lo + 1e-3, hi - sl) + 1e-6, ST)
    if len(grid) == 0 or hi - lo < sl: problems.append(f"줄{it['k']} [{mm(lo)}~{mm(hi)}] 이 조각 하나({sl:.1f}초)보다 짧음"); continue
    ok = free_mask(z, grid, sl)
    ideal = [lo + (hi - lo - sl) * (j / (n - 1) if n > 1 else 0.0) for j in range(n)]
    base = np.array([2.0 * dark(g, g + sl) + (1.5 * speech(g, g + sl) if it["kind"] == "A" else 0.0) for g in grid])
    sh = int(math.ceil((sl + GAP) / ST))
    INF = 1e9; prev = None; back = []
    for j in range(n):
        c = np.where(ok, np.abs(grid - ideal[j]) / max(3.0, (hi - lo) / n) + base, INF)
        if prev is None: f = c; back.append(None)
        else:
            f = np.full(len(grid), INF); bk = np.zeros(len(grid), int)
            pm = np.minimum.accumulate(prev); am = np.zeros(len(grid), int); best = 0
            for q in range(len(grid)):
                if prev[q] < prev[best]: best = q
                am[q] = best
            f[sh:] = c[sh:] + pm[:-sh] if sh < len(grid) else INF
            bk[sh:] = am[:-sh] if sh < len(grid) else 0
            back.append(bk)
        prev = f
    if prev is None or prev.min() >= INF / 2:
        need = n * sl + (n - 1) * GAP
        problems.append(f"줄{it['k']} {it['kind']} 「{it.get('text', '')[:24]}」 [{mm(lo)}~{mm(hi)}] 안에 조각 {n}개({Lw:.1f}초) 놓을 자리 없음 — 구간 {hi - lo:.1f}초, 필요 약 {need:.1f}초(다른 줄과 3초 간격 포함)")
        continue
    q = int(np.argmin(prev)); pos = [0] * n
    for j in range(n - 1, -1, -1):
        pos[j] = q
        if back[j] is not None: q = int(back[j][q])
    ps = [float(grid[p]) for p in pos]
    for j in range(n):
        p2 = shot_snap(ps[j], sl, lo, hi)
        nxt_ok = j == 0 or p2 >= ps[j - 1] + sl + GAP - 1e-6        # 당기면 앞 조각과 3초 간격 확인
        if nxt_ok and all(not (p2 < y + GAP and p2 + sl + GAP > x) for x, y in used[z]): ps[j] = p2
    for j in range(n):
        a = it["t"] + Lw * j; b = it["t"] + Lw * (j + 1)
        W.append(dict({"a": round(a, 3), "b": round(b, 3), "s": round(ps[j], 3), "kind": "A", "k": it["k"], "z": z}, **it["opt"])); used[z].append((ps[j], ps[j] + sl))
        if dark(ps[j], ps[j] + sl) >= 0.75: problems.append(f"줄{it['k']} 조각 {mm(a)} 원본 {mm(ps[j])} 까만 화면 {dark(ps[j], ps[j] + sl):.1f}초")
W.sort(key=lambda w: w["a"])

# ── 4. 검사 (계획 단계에서 보장해야 할 것)
for i in range(len(W) - 1):
    if abs(W[i]["b"] - W[i + 1]["a"]) > 0.005: problems.append(f"화면 시간 끊김 {mm(W[i]['b'])} → {mm(W[i + 1]['a'])}")
for z in used:
    sp = sorted(used[z])
    for x, y in zip(sp, sp[1:]):
        if y[0] - x[1] < GAP - 0.01: problems.append(f"{z} 원본 3초 간격 어김 {mm(x[1])} / {mm(y[0])}")
fl = [w for w in W if w["b"] - w["a"] < 0.5]
for w in fl: problems.append(f"0.5초 안 되는 깜빡 조각 {mm(w['a'])} ({w['b'] - w['a']:.2f}초)")
nar = [(it["ni"], it["t"] + it["lead"], it["d"]) for it in items if it["kind"] == "N"]
NS = sum(d for _, _, d in nar); DS = sum(it["d"] for it in items if it["kind"] == "D")   # 대사 창 화면 초
srcuse = sum(min(y, SRCLEN) - x for z in used for x, y in used[z])
rep = [f"화면 {mm(BODY)} ({BODY:.0f}초) · 원본 {SRCLEN / 60:.0f}분의 {100 * BODY / SRCLEN:.0f}% · 나레 {len(nar)}줄 {NS:.0f}초 = {100 * NS / BODY:.0f}% · 대사 창 {sum(1 for it in items if it['kind'] == 'D')}개 {DS:.0f}초 · 조각 {len(W)} · 원본 쓴 양 {srcuse / 60:.1f}분",
       f"가장 긴 조각 {max(w['b'] - w['a'] for w in W):.2f}초 · 대사 창 최장 {max([it['d'] for it in items if it['kind'] == 'D'] or [0]):.2f}초"]
rep += [f"✗ {p}" for p in problems]
open("plan_report.txt", "w", encoding="utf-8").write("\n".join(rep) + "\n")
print("\n".join(rep[:2])); print(f"문제 {len(problems)}")
for p in problems[:60]: print("  ✗", p)
if not DRY:
    json.dump(W, open("windows.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump([{"ni": n, "t": round(t, 3), "d": round(d, 3)} for n, t, d in nar], open("narr_place.json", "w"), indent=0)
else:
    json.dump(W, open("windows_dry.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
sys.exit(1 if problems else 0)
