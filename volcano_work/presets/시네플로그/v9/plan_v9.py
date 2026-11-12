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
# ⛔11-03 사용자 「영화 원본 주면 안되는거는 시작도 하지마」 — 금지 회사 작품(../blocked_studios.txt)이면 계획부터 멈춤
from blocked import stop_if_blocked
stop_if_blocked(os.path.basename(os.getcwd()), str(CFG.get("src", "")), str(CFG.get("title", "")))
SRC, SRCLEN = CFG["src"], CFG["srclen"]
SPD, GAP, MAXC = 1.05, 3.0, 2.9
# ★10-31 드루와 09 재편집: ep.json "tail_src" = [시작, 끝](사용자 예전 편 화면을 원본 끝에 이어 붙인 구간) 안 조각끼리는 "tail_gap"(기본 GAP) 간격 — 재료가 1,231초뿐이라 3초면 5분밖에 못 씀
TAIL0, TGAP = (CFG.get("tail_src") or [1e18])[0], CFG.get("tail_gap", GAP)
def gp(*ts): return TGAP if min(ts) >= TAIL0 - 1e-6 else GAP
DMAX, DSPD = CFG.get("dmax", 3.0), CFG.get("dspd", 1.05)     # 대사 창 화면 최장(초)·배속 (10-14 CID)
# ★11-01 드루와 09 사용자 「장면이 끝날때 너무 짧게 뚝 끊겨버려」「그래서 정신이 없어」 → ep.json(기본 0 = 예전 그대로, 드라마는 drama_kit 값):
#   "d_tail"(화면 초): 대사 말끝 뒤 원본 화면·소리를 더 흘림(표정·반응 여운). 다음 낱말 0.15초 앞·다음 컷 0.05초 앞까지만, 대사 창 합계 DMAX+"d_tail_over"(기본 0 — 관문 ⑫ CID 3초, 10-14 사용자 「1」) 안
#   "d_fade"(초): 대사 창 끝 소리 줄이기(기본 0.05) — 여운 구간에 걸쳐 줄인다
#   "scene_pad"(초): 장면이 바뀌는 곳(다음 줄 원본이 "scene_jump" 초(기본 20) 넘게 떨어짐) 앞 줄 그림을 더 둠 — 숨 돌릴 틈
# ★11-04 시네플로그: 여운 기본값은 새 방식 편(ep.json 에 d_fill 있음, movie_template)만. 옛 편은 다시 계획해도 조각이 그대로다(33편으로 확인).
NEWSTYLE = "d_fill" in CFG
DTAIL, DTOVER, DFADE = CFG.get("d_tail", 0.6 if NEWSTYLE else 0.0), CFG.get("d_tail_over", 0.0), CFG.get("d_fade", 0.3 if NEWSTYLE else 0.05)   # 다른 PC 11-02 사용자 「장면 끝나는 시점을 이렇게 하니까 좋아」
SCPAD, SCJUMP = CFG.get("scene_pad", 0.3 if NEWSTYLE else 0.0), CFG.get("scene_jump", 20.0)
CPS = 6.5          # 제미나이 Ludo 실측(16 핀치 148조각): 띄어쓰기 뺀 글자 6.51자/초
DRY = "--dry" in sys.argv
# ★★★★★11-07 33 콜래트럴 박제(사용자 「너 왜이렇게만들었어?」→「틀린거 다 저장하고 박제해」, README 맨 위):
#   옛 방식은 나레 밑 조각을 범위(중앙 80초·최대 256초)의 처음·가운데·끝에 고르게 깔아서 마지막 조각이 장면 결말에서 뽑히고
#   그 뒤에 범위 앞쪽 대사가 붙어 되감겼다(68블록 중 46 「결과 먼저」). 이제 기본은:
#   ① 나레 구간(문장마다·조각마다)은 n_span(기본 30초) 안 — 넘으면 실패 ② 조각은 구간 앞에서부터 차례로(고르게 깔기 금지)
#   ③ 나레·소리 장면 그림의 원본 끝은 다음 대사 원본 시작을 넘지 못함(구간을 거기서 자름, 구간 전체가 뒤면 실패 — 「결과 먼저」)
#   ④ 이어 붙은 조각끼리 원본이 rewind_max(기본 10초) 넘게 되감기면 실패 ⑤ 같은 내용 나레 연달아 경고 ⑥ text_scan.json 글자 조각은 반전 안 함
#   줄 옵션: {"sent": True} = 세 번째 칸 [(a,b)…] 가 문장마다 구간(조각은 문장이 말해지는 시각으로 나눔) · {"order_ok": "이유"} = ③④ 예외(이유 필수)
#   {"wide_ok": "이유"} = ① 예외. ep.json "legacy_spread": true 면 옛 방식 그대로(옛 편 재현용).
LEGACY = bool(CFG.get("legacy_spread"))
NSPAN, REWIND = CFG.get("n_span", 30.0), CFG.get("rewind_max", 10.0)
def sent_split(text):
    """문장 시작 글자 위치들 — . ? ! 뒤(따옴표·괄호 붙어도) 공백에서 끊음"""
    st = [0]
    for m in re.finditer(r"[.?!…]+[\"'”’)]*\s+", text): st.append(m.end())
    return [i for i in st if i < len(text.rstrip())]
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
        if isinstance(x[2], (list, tuple)):
            if opt.get("sent"):                      # ★11-07 문장마다 구간 — 문장 칸은 (a,b) 또는 [(a,b),(a,b)…](한 문장 속 동작이 여럿이면 조각 차례대로)
                rs = [[(float(e[0]), float(e[1]))] if not isinstance(e[0], (list, tuple)) else [(float(a), float(b)) for a, b in e] for e in x[2]]
                ss = sent_split(x[1])
                if len(ss) != len(rs): problems.append(f"줄{k} 「{x[1][:24]}」 문장 {len(ss)}개인데 sent 구간 {len(rs)}개 — 문장마다 하나씩")
                it.update(sent_parts=rs, a=min(a for r in rs for a, _ in r), b=max(b for r in rs for _, b in r))
            else:
                rs = [(float(a), float(b)) for a, b in x[2]]
                it.update(parts=rs, a=float(x[2][0][0]), b=float(x[2][-1][1]))
        else: it.update(a=float(x[2]), b=float(x[3]))
        w = f"narr/n{ni:03d}.wav"
        same = os.path.exists(w) and json.load(open(w[:-4] + ".json", encoding="utf-8")).get("text") == x[1]   # --dry 도 글이 같은 녹음은 실제 길이(10-14 줄 바꾼 뒤 번호 다시 매김)
        it["d"] = dur(w) if same or (os.path.exists(w) and not DRY) else len(re.sub(r"\s", "", x[1])) / CPS
        # 문장 시작 시각(나레 wav 기준 초) — 글자 정렬(narr/nNNN.json chars·st)이 있으면 그것, 없으면 글자 수 비례
        ss = sent_split(x[1]); al = json.load(open(w[:-4] + ".json", encoding="utf-8")) if same else None
        if al and len(al.get("chars", [])) == len(x[1]) and al.get("st"): it["sent_t"] = [float(al["st"][i]) for i in ss]
        else:
            nz = [len(re.sub(r"\s", "", x[1][:i])) for i in ss]; tot = max(1, len(re.sub(r"\s", "", x[1])))
            it["sent_t"] = [it["d"] * c / tot for c in nz]
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
# 11-01 대사 여운(d_tail): 대화가 끝나는 대사(다음 줄이 나레·원본 소리이거나 다른 장면)만 — 주고받는 대사끼리는 그대로 딱 붙인다
#   다음 낱말·다음 컷·같은 구역 다른 대사의 원본 3초 간격 안에서만
def _jump0(x, y): return abs((y["s"] if y["kind"] == "D" else y["a"]) - (x["e"] if x["kind"] == "D" else x["b"])) > SCJUMP
# ★11-03 사용자 「원본 대사가 나올때도 3초가 한장면으로 이어져야하는데 이것도 자른것같던데」(37 우주전쟁: 대사 창 평균 2.1초, 1.5초 미만 49곳)
#   → "d_fill"(화면 초, 기본 = DMAX 3.0): 대사 창을 말끝 뒤 같은 장면 원본(표정·반응)으로 이 길이까지 채운다. 주고받는 대사 사이도 채움.
#   멈추는 곳: 다른 사람 말(다음 낱말 0.15초 앞)·같은 구역 다른 대사 3초 간격·원본 컷(컷 뒤가 0.5초 안 되면 컷 0.05초 앞 — 깜빡 금지).
#   옛 판(말끝 + 0.6초만)으로 돌리려면 ep.json "d_fill": 0.
DFILL = CFG.get("d_fill", 0.0)   # ★11-03 사용자 「아직 프리셋에 반영하지는 마. 만들어보고 괜찮으면 할거야」 → 기본 꺼짐, 시험 편만 ep.json "d_fill": 3.0
if DTAIL > 0 or DFILL > 0:
    for i, it in enumerate(items):
        if it["kind"] != "D": continue
        y = items[i + 1] if i + 1 < len(items) else None
        if DFILL <= 0 and y is not None and y["kind"] == "D" and y["zone"] == it["zone"] and not _jump0(it, y): continue
        if it["opt"].get("no_tail"): continue                     # 대본 줄 {"no_tail": True} — 옆 나레 줄 원본 자리가 모자랄 때(34 리셋)
        s2, e2 = it["s"], it["e"]
        want = max(DTAIL * DSPD, DFILL * DSPD - (e2 - s2))
        nw = env.ws[env.ws > e2 - 0.03]; nc = cuts[cuts > e2 + 0.02]
        od = [o["s"] for o in items if o is not it and o["kind"] == "D" and o["zone"] == it["zone"] and o["s"] > e2 - 0.01]
        # ★11-03 사용자 「그걸 자르면 안돼」 — 3초 안에 바로 이어지는 상대 말(다음 대사 줄)은 멈춰서 끊지 말고 같은 대사 창에 묶어 자막까지(대본 단계).
        #   묶을 수 있는데 안 묶었으면 문제로 올려 대본을 고치게 한다(묶으면 그 말까지 3초 한 장면).
        if DFILL > 0 and len(nw) and nw[0] - e2 < DFILL * DSPD - (e2 - s2):
            nxt = [l for l in L.values() if l["ws"] is not None and abs(l["ws"] - nw[0]) < 0.3 and l["id"] not in it["ids"]]
            used_ids = {j for o in items if o["kind"] == "D" for j in o["ids"]}
            for l in nxt[:1]:
                if l["id"] in used_ids: continue
                if l["we"] - s2 <= DMAX * DSPD + 1e-6:
                    problems.append(f"줄{it['k']} 대사 {it['ids']} 바로 뒤 상대 말 [{l['id']}] 「{l['en']}」 이 3초 안에 들어감 — 자르지 말고 묶기: "
                                    f"('D', {it['ids'] + [l['id']]}, '{it['ko']} / <그 말 자막>') (11-03 「그걸 자르면 안돼」)")
        lim = min((nw[0] - 0.15 - e2) if len(nw) else 9e9, (DMAX + DTOVER) * DSPD - (e2 - s2),
                  (min(od) - gp(e2, min(od)) - e2) if od else 9e9, want)
        if DFILL > 0:   # 컷을 넘어도 원본 그대로 이어지는 것 — 컷 뒤 그림이 0.5초 안 되게 끝나면 깜빡이므로 그 컷 앞에서 멈춤
            for c in nc:
                if c - e2 >= lim: break
                if e2 + lim - c < 0.5: lim = c - 0.05 - e2; break
        else:
            lim = min(lim, (nc[0] - 0.05 - e2) if len(nc) else 9e9)
        room = lim
        if room >= 0.15: it["tail"] = round(room, 3); it["d"] = (e2 + room - s2) / DSPD
t = 0.0
def jump(i):
    """items[i] 다음 줄이 다른 장면(원본 SCJUMP 초 넘게 떨어짐)인가 — 같은 구역 안만"""
    if SCPAD <= 0 or i + 1 >= len(items) or items[i + 1]["zone"] != items[i]["zone"]: return False
    x, y = items[i], items[i + 1]
    return abs((y["s"] if y["kind"] == "D" else y["a"]) - (x["e"] if x["kind"] == "D" else x["b"])) > SCJUMP
for i, it in enumerate(items):
    it["t"] = round(t, 3)
    prv = items[i - 1]["kind"] if i else "A"; nxt = items[i + 1]["kind"] if i + 1 < len(items) else "A"
    it["lead"] = 0.15 if (prv == "D" and it["kind"] == "N") else 0.0
    pad = PAD.get((it["kind"], nxt), 0.0)
    # 장면 바뀜 숨은 그 줄 조각 수가 늘지 않을 때만(조각이 하나 늘면 원본 자리가 3초+ 더 필요 — 34 리셋 dry 「자리 없음」 3줄)
    fits = lambda extra: math.ceil((it["lead"] + it["d"] + pad + extra) / MAXC - 1e-6) == math.ceil((it["lead"] + it["d"] + pad) / MAXC - 1e-6)
    if it["kind"] == "N" and i and items[i - 1]["kind"] == "D" and jump(i - 1) and fits(SCPAD): it["lead"] += SCPAD   # 대사로 끝난 장면 → 새 장면 그림 먼저 깔고 나레는 늦게
    if it["kind"] != "D" and jump(i) and fits(SCPAD): pad += SCPAD; it["scene_end"] = True
    it["T"] = round(t + it["lead"] + it["d"] + pad, 3)       # 이 줄 그림이 차지하는 화면 끝(다음 줄 시작)
    t = it["T"]
BODY = t

# ── 2. 대사 창(고정) → 구역별 원본 사용 구간
used = {"hook": [], "main": [], "outro": []}
W = []
for it in items:
    if it["kind"] != "D": continue
    w = {"a": it["t"], "b": it["T"], "s": round(it["s"], 3), "kind": "D", "k": it["k"], "ko": it["ko"], "sub1": round(it["sl"], 3), "z": it["zone"]}
    if it.get("tail"): w["fo"] = round(max(0.05, min(DFADE, it["tail"] / DSPD)), 3)   # 11-01 여운 구간 안에서만 소리 줄이기(말끝은 그대로)
    w.update(it["opt"])                                            # 10-14 대사 창도 {"noflip": True} (뉴스 화면·모니터 글자 — 01 헤즈 오브 스테이트)
    if DSPD != 1: w["rate"] = DSPD                                 # build cut: 영상 setpts + 소리 atempo 같이 · 자막 시각은 원본 기준(build 가 /rate)
    parts = [p.strip() for p in it["ko"].split(" / ")]
    if len(parts) > 1 and len(parts) == len(it["ids"]):
        st = [max(0.05, L[i]["ws"] - it["s"]) for i in it["ids"]] + [it["sl"]]          # 원본 기준 초(build 가 /rate)
        w["subs"] = [[parts[j], round(st[j] if j else 0.05, 3), round(st[j + 1], 3)] for j in range(len(parts))]
    W.append(w); used[it["zone"]].append((it["s"], it["s"] + (it["T"] - it["t"]) * DSPD))
# ★11-03 핵심 장면 이어 가기 — 사용자 「원본 6초가 나오면 중간에 짧게 나래이션을 넣는 방식」「중요 핵심 장면이 끈어지지 않게 만들어야할때만 이방법을 쓰고」
#   대본 ("D", …) → ("N", "짧은 나레", a, b, {"cont": True}) → ("D", …): 나레 밑 그림이 앞 대사 창 원본 바로 뒤를 그대로 이어 가고(반전·확대는 앞 대사와 같게, 원본 소리는 나레 밑에서 작게),
#   다음 대사까지 한 장면으로 이어진다. 이 사이만 3초 간격 예외. 나레는 조각 하나(2.9초 안) — 짧게.
LINKS = []                                   # (구역, 앞 끝 원본초, 뒤 시작 원본초) — 3초 간격 검사에서 빼는 이음
CONT_D = set()                               # 핵심 장면 이음으로 묶인 (앞 대사 k, 뒤 대사 k)
for i, it in enumerate(items):
    if it["kind"] == "N" and it["opt"].get("cont") and 0 < i < len(items) - 1 and items[i - 1]["kind"] == "D" and items[i + 1]["kind"] == "D":
        CONT_D.add((items[i - 1]["s"], items[i + 1]["s"]))
def _linked(z, x1, y0): return any(lz == z and abs(lx - x1) < 0.05 and abs(ly - y0) < 0.05 for lz, lx, ly in LINKS)
for z in used:
    sp = sorted(used[z])
    for x, y in zip(sp, sp[1:]):
        if any(abs(x[0] - p) < 1e-3 and abs(y[0] - q) < 1e-3 for p, q in CONT_D): continue
        if y[0] - x[1] < gp(x[0], y[0]) - 0.01: problems.append(f"{z} 대사끼리 원본 3초 간격 어김 {mm(x[0])}~{mm(x[1])} / {mm(y[0])}")

# ── 3. 나레·액션 줄: [a,b] 안에서 순서대로 조각 고르기 (DP, 0.1초 칸)
ST = 0.1
def free_mask(z, grid, sl):
    ok = np.ones(len(grid), bool)
    for x, y in used[z]: g = gp(x, float(grid[0])); ok &= ~((grid < y + g) & (grid + sl + g > x))
    return ok
SNAP_FWD = CFG.get("snap_fwd", True)
def shot_snap(p, sl, lo, hi):
    """조각 시작이 컷 시작 바로 뒤(0.6초 안)면 그 컷 시작으로 당긴다 — 다음 컷으로 밀면 다른 그림이 된다(10-13 「레이더에 표적이」 밑에 뱃머리)
    ★11-07 32v2: 조각 첫머리에 앞 컷 꼬리만 잠깐 걸리면(컷이 시작 뒤 0.5초·조각 길이 40% 안) 그 컷 뒤로 민다 — 조각 대부분이 이미 뒤 컷이라 그림은 그대로,
    줄 첫 프레임에 앞 장면이 번쩍 나오던 것만 없어진다(32 v2 판정 「부분」 59줄 중 약 13줄이 이것). ep.json "snap_fwd": false 면 옛 동작."""
    if SNAP_FWD:
        c = cuts[(cuts > p + 0.02) & (cuts <= p + min(0.5, sl * 0.4))]
        if len(c) and c[-1] + 0.06 + sl <= hi + 1e-6: return float(c[-1]) + 0.06
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
        c = [g for g in np.arange(lo, hi - sl + 1e-6, ST) if all(not (g < y + gp(x, g) and g + sl + gp(x, g) > x) for x, y in used[z] + mine)]
        if not c: problems.append(f"줄{it['k']} 「{it.get('text', '')[:24]}」 조각{j + 1} [{mm(lo)}~{mm(hi)}] 에 {sl:.1f}초 자리 없음"); return None
        g = min(c, key=lambda g: 2.0 * dark(g, g + sl) + abs(g - lo) * 0.05); ps.append(float(g))
    return ps, n, Lw, sl
# ★11-07 ①③: 나레 구간 폭 검사 · 다음 대사 원본 시작에서 구간 자르기(결과 먼저 금지)
def _ranges(it):
    if it.get("sent_parts"): return [r for sub in it["sent_parts"] for r in sub]
    if it.get("parts"): return it["parts"]
    return [(it["a"], it["b"])]
if not LEGACY:
    for ii, it in enumerate(items):
        if it["kind"] == "D" or it["zone"] == "outro" or it["opt"].get("cont"): continue
        if it["kind"] == "N" and not it["opt"].get("wide_ok"):
            for a, b in _ranges(it):
                if b - a > NSPAN + 1e-6: problems.append(f"줄{it['k']} 나레 「{it['text'][:24]}」 구간 {mm(a)}~{mm(b)} {b - a:.0f}초 — {NSPAN:g}초 넘음(문장마다 그 장면을 좁게, {{'sent': True}} · 11-07)")
        nd = next((y for y in items[ii + 1:] if y["kind"] == "D" or y["zone"] != it["zone"]), None)
        if nd is None or nd["zone"] != it["zone"]: continue
        why = it["opt"].get("order_ok")
        if why: continue
        it["lim"] = nd["s"]
        for a, b in _ranges(it):
            if a >= nd["s"] - 0.05:
                what = f"나레 「{it['text'][:24]}」" if it["kind"] == "N" else f"소리 장면 A {mm(a)}"
                problems.append(f"줄{it['k']} 결과 먼저: {what} 구간 {mm(a)}~{mm(b)} 이 다음 대사(줄{nd['k']} 원본 {mm(nd['s'])}) 보다 뒤 — 대사 뒤로 옮기거나 구간을 대사 앞으로(11-07)")
                it["blocked"] = True; break
def _clip(it, a, b):
    lim = it.get("lim")
    return (a, min(b, lim)) if lim is not None else (a, b)
def place_seq(it, z, pieces):
    """★11-07 조각을 구간 앞에서부터 차례로 — pieces = [(화면a, 화면b, 원본lo, 원본hi)…]. 앞 조각보다 뒤(이야기 순서)·3초 간격·어두움 피하기"""
    ps = []; last = None
    for j, (a, b, lo, hi) in enumerate(pieces):
        sl = (b - a) * SPD; mine = [(q, q + (pieces[m][1] - pieces[m][0]) * SPD) for m, q in enumerate(ps)]
        def okg(g): return all(not (g < y + gp(x, g) and g + sl + gp(x, g) > x) for x, y in used[z] + mine)
        grid = np.arange(lo, hi - sl + 1e-6, ST)
        c = [g for g in grid if okg(g) and (last is None or g >= last - 1e-6)]
        if not c: c = [g for g in grid if okg(g)]
        if not c:
            problems.append(f"줄{it['k']} 「{it.get('text', '')[:24]}」 조각{j + 1} [{mm(lo)}~{mm(hi)}] 에 {sl:.1f}초 자리 없음" + (f"(다음 대사 {mm(it['lim'])} 앞에서 자름)" if it.get("lim") is not None and hi >= it["lim"] - 1e-6 else ""))
            return None
        g = min(c, key=lambda g: 2.0 * dark(g, g + sl) + (g - lo) * 0.05)
        g2 = shot_snap(g, sl, lo, hi)
        if okg(g2) and (last is None or g2 >= last - 1e-6): g = g2
        ps.append(float(g)); last = g + sl + gp(g)
    return ps
for ii, it in enumerate(items):
    if it["kind"] == "D" or it.get("blocked"): continue
    d = it["T"] - it["t"]; n = max(1, math.ceil(d / MAXC - 1e-6)); Lw = d / n; sl = Lw * SPD
    lo, hi = _clip(it, it["a"], it["b"]); z = it["zone"]
    if it.get("sent_parts") and not it["opt"].get("cont"):     # ★11-07 문장마다 구간: 화면 시간을 문장 시작 시각에서 나누고, 문장 조각은 그 문장 구간에서
        u = [it["t"]] + [it["t"] + it["lead"] + s for s in it["sent_t"][1:]] + [it["T"]]
        segs = [[u[q], u[q + 1], q] for q in range(len(u) - 1)]
        while len(segs) > 1 and any(s[1] - s[0] < 0.6 for s in segs):          # 0.6초 안 되는 문장 몫은 이웃 문장에 붙임(깜빡 조각 금지)
            q = next(i for i, s in enumerate(segs) if s[1] - s[0] < 0.6)
            if q > 0: segs[q - 1][1] = segs[q][1]
            else: segs[1][0] = segs[0][0]
            segs.pop(q)
        pieces = []
        for a0, b0, q in segs:
            sub = it["sent_parts"][min(q, len(it["sent_parts"]) - 1)]
            nq = max(1, math.ceil((b0 - a0) / MAXC - 1e-6), min(len(sub), int((b0 - a0) / 0.6))); Lq = (b0 - a0) / nq   # 동작 수만큼은 조각을 나눔(0.6초 안 되게는 안 함)
            for j in range(nq):
                rlo, rhi = _clip(it, *sub[min(j, len(sub) - 1)])
                pieces.append((a0 + Lq * j, a0 + Lq * (j + 1), rlo, rhi))
        ps = place_seq(it, z, pieces)
        if ps is None: continue
        for (a, b, _, _), s in zip(pieces, ps):
            W.append(dict({"a": round(a, 3), "b": round(b, 3), "s": round(s, 3), "kind": "A", "k": it["k"], "z": z}, **it["opt"])); used[z].append((s, s + (b - a) * SPD))
        continue
    if not LEGACY and not it["opt"].get("cont") and it.get("parts"):   # 조각마다 구간(옛 꼴) — 다음 대사에서 자르고 차례로
        P = [_clip(it, a, b) for a, b in it["parts"]]
        if len(P) != n: problems.append(f"줄{it['k']} 「{it.get('text', '')[:24]}」 조각 {n}개인데 parts 구간 {len(P)}개 — {{'sent': True}}(문장마다 구간)로 쓸 것"); continue
        pieces = [(it["t"] + Lw * j, it["t"] + Lw * (j + 1), P[j][0], P[j][1]) for j in range(n)]
        if Lw > MAXC + 1e-6: problems.append(f"줄{it['k']} 조각 {n}개로는 {Lw:.1f}초씩 — 2.9초 넘음"); continue
        ps = place_seq(it, z, pieces)
        if ps is None: continue
        for (a, b, _, _), s in zip(pieces, ps):
            W.append(dict({"a": round(a, 3), "b": round(b, 3), "s": round(s, 3), "kind": "A", "k": it["k"], "z": z}, **it["opt"])); used[z].append((s, s + (b - a) * SPD))
        continue
    if not LEGACY and not it["opt"].get("cont"):                   # 한 구간: 앞에서부터 차례로(고르게 깔기 금지)
        if hi - lo < sl: problems.append(f"줄{it['k']} [{mm(lo)}~{mm(hi)}] 이 조각 하나({sl:.1f}초)보다 짧음" + (f" — 다음 대사 {mm(it['lim'])} 앞에서 자름(11-07 결과 먼저 금지)" if it.get("lim") is not None and it["b"] > it["lim"] else "")); continue
        pieces = [(it["t"] + Lw * j, it["t"] + Lw * (j + 1), lo, hi) for j in range(n)]
        ps = place_seq(it, z, pieces)
        if ps is None: continue
        for (a, b, _, _), s in zip(pieces, ps):
            W.append(dict({"a": round(a, 3), "b": round(b, 3), "s": round(s, 3), "kind": "A", "k": it["k"], "z": z}, **it["opt"])); used[z].append((s, s + sl))
            if dark(s, s + sl) >= 0.75: problems.append(f"줄{it['k']} 조각 {mm(a)} 원본 {mm(s)} 까만 화면 {dark(s, s + sl):.1f}초")
        continue
    if it["opt"].get("cont"):                # ★11-03 핵심 장면 이어 가기(위 설명)
        pv = items[ii - 1] if ii else None; nx = items[ii + 1] if ii + 1 < len(items) else None
        if pv is None or pv["kind"] != "D":
            problems.append(f"줄{it['k']} {{'cont': True}} 는 대사(D) 바로 뒤 나레에만"); continue
        if d > MAXC + 1e-6:
            problems.append(f"줄{it['k']} 핵심 장면 이음 나레 「{it.get('text', '')[:24]}」 화면 {d:.1f}초 — {MAXC}초 안으로 짧게(나레 줄이기)"); continue
        src_end = pv["s"] + (pv["T"] - pv["t"]) * DSPD; sl = d * SPD; st0 = src_end
        if nx is not None and nx["kind"] == "D" and nx["zone"] == z:
            if nx["s"] < src_end + 0.2: problems.append(f"줄{it['k']} 핵심 장면 이음: 다음 대사 원본 {mm(nx['s'])} 이 앞 대사 끝 {mm(src_end)} 보다 앞"); continue
            st0 = max(src_end, nx["s"] - sl)               # 다음 대사 바로 앞에서 끝나게(남는 틈은 앞으로 건너뜀)
            if st0 + sl > nx["s"] + 0.05: problems.append(f"줄{it['k']} 핵심 장면 이음: 나레 그림({sl:.1f}초)이 다음 대사와 {st0 + sl - nx['s']:.1f}초 겹침 — 나레를 짧게"); continue
            if st0 - src_end > 3.0 and nx["s"] - (src_end + 3.0 + sl) <= 3.0: st0 = src_end + 3.0   # ★11-03 41: 틈이 3초 넘으면 앞뒤로 나눠 건너뜀(앞 3초·뒤 나머지)
            LINKS.append((z, st0 + sl, nx["s"]))
            if st0 - src_end > 3.0: problems.append(f"줄{it['k']} 핵심 장면 이음: 앞 대사 끝과 {st0 - src_end:.1f}초 건너뜀(3초 넘음) — 나레를 늘리거나 다음 대사를 앞으로")
        LINKS.append((z, src_end, st0))
        nf = bool(pv["opt"].get("noflip"))          # 앞 대사 창과 같은 반전·확대여야 한 장면으로 보임
        if nx is not None and nx["kind"] == "D" and bool(nx["opt"].get("noflip")) != nf: problems.append(f"줄{it['k']} 핵심 장면 이음: 앞뒤 대사 noflip 이 달라 화면이 뒤집힘 — 둘 다 같게")
        W.append(dict(dict({"a": round(it["t"], 3), "b": round(it["T"], 3), "s": round(st0, 3), "kind": "A", "k": it["k"], "z": z, "cont": True}, **it["opt"]), noflip=nf))
        used[z].append((st0, st0 + sl)); continue
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
    sh = int(math.ceil((sl + gp(lo)) / ST))
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
        nxt_ok = j == 0 or p2 >= ps[j - 1] + sl + gp(ps[j - 1], p2) - 1e-6        # 당기면 앞 조각과 3초 간격 확인
        if nxt_ok and all(not (p2 < y + gp(x, p2) and p2 + sl + gp(x, p2) > x) for x, y in used[z]): ps[j] = p2
    for j in range(n):
        a = it["t"] + Lw * j; b = it["t"] + Lw * (j + 1)
        W.append(dict({"a": round(a, 3), "b": round(b, 3), "s": round(ps[j], 3), "kind": "A", "k": it["k"], "z": z}, **it["opt"])); used[z].append((ps[j], ps[j] + sl))
        if dark(ps[j], ps[j] + sl) >= 0.75: problems.append(f"줄{it['k']} 조각 {mm(a)} 원본 {mm(ps[j])} 까만 화면 {dark(ps[j], ps[j] + sl):.1f}초")
W.sort(key=lambda w: w["a"])
# ★11-07 ⑥ 글자 조각은 반전 안 함 — text_scan.json(prep/textflip.py · 사람이 본 것) 의 원본 구간과 겹치는 조각
TS = json.load(open(CFG.get("text_scan", "text_scan.json"), encoding="utf-8")) if os.path.exists(CFG.get("text_scan", "text_scan.json")) else {}
TXT = [(float(a), float(b)) for a, b, *_ in TS.get("text", [])]; ntx = 0
def _sl(w): return (w["b"] - w["a"]) * w.get("rate", SPD if w["kind"] == "A" else 1.0)
for w in W:
    if not w.get("noflip") and any(w["s"] < b and w["s"] + _sl(w) > a for a, b in TXT): w["noflip"] = True; w["noflip_text"] = True; ntx += 1
# ★11-07 ④ 되감기 · 결과 먼저(나레 블록 그림보다 10초+ 앞선 대사가 뒤에 나옴 — sync_check ① 와 같은 잣대)
KOPT = {it["k"]: it["opt"] for it in items}
if not LEGACY:
    def _se(w): return w["s"] + _sl(w)
    for x, y in zip(W, W[1:]):
        if x["z"] != "main" or y["z"] != "main" or KOPT.get(y["k"], {}).get("order_ok") or KOPT.get(x["k"], {}).get("order_ok"): continue
        if y["s"] < _se(x) - REWIND: problems.append(f"되감기: 화면 {mm(y['a'])} 줄{y['k']} 원본 {mm(y['s'])} 가 앞 조각(줄{x['k']}) 원본 끝 {mm(_se(x))} 보다 {_se(x) - y['s']:.0f}초 앞 — 줄 순서를 원본 순서로(11-07)")
    NB = [it for it in items if it["kind"] == "N" and it["zone"] != "outro"]
    for i, it in enumerate(NB):
        As = [w for w in W if w["k"] == it["k"] and w["kind"] == "A"]
        if not As or it["opt"].get("order_ok"): continue
        mx = max(w["s"] for w in As); nxt = NB[i + 1]["t"] if i + 1 < len(NB) else 1e9
        for w in W:
            if w["kind"] == "D" and it["T"] - 0.05 <= w["a"] < nxt and w["s"] < mx - 10:
                problems.append(f"결과 먼저: 줄{it['k']} 나레 「{it['text'][:24]}」 그림(원본 {mm(mx)})이 뒤 대사 줄{w['k']}(원본 {mm(w['s'])}) 보다 {mx - w['s']:.0f}초 뒤 장면"); break
# ★11-07 ⑤ 같은 내용 나레 연달아(경고) — 글자 두 개씩 겹침
def _bg(s): s = re.sub(r"[\s.,!?…'\"“”‘’]", "", s); return {s[i:i + 2] for i in range(len(s) - 1)}
WARN = []
NN = [it for it in items if it["kind"] == "N"]
for i, x in enumerate(NN):
    for y in NN[i + 1:i + 3]:
        A_, B_ = _bg(x["text"]), _bg(y["text"])
        j = len(A_ & B_) / max(1, min(len(A_), len(B_)))
        if j >= 0.45: WARN.append(f"같은 내용 나레 연달아? 줄{x['k']} 「{x['text'][:28]}」 ↔ 줄{y['k']} 「{y['text'][:28]}」 (겹침 {j:.2f})")

# ── 4. 검사 (계획 단계에서 보장해야 할 것)
for i in range(len(W) - 1):
    if abs(W[i]["b"] - W[i + 1]["a"]) > 0.005: problems.append(f"화면 시간 끊김 {mm(W[i]['b'])} → {mm(W[i + 1]['a'])}")
for z in used:
    sp = sorted(used[z])
    for x, y in zip(sp, sp[1:]):
        if _linked(z, x[1], y[0]) or any(abs(x[0] - p) < 1e-3 and abs(y[0] - q) < 1e-3 for p, q in CONT_D): continue   # 11-03 핵심 장면 이음
        if y[0] - x[1] < gp(x[0], y[0]) - 0.01: problems.append(f"{z} 원본 3초 간격 어김 {mm(x[1])} / {mm(y[0])}")
fl = [w for w in W if w["b"] - w["a"] < 0.5]
for w in fl: problems.append(f"0.5초 안 되는 깜빡 조각 {mm(w['a'])} ({w['b'] - w['a']:.2f}초)")
nar = [(it["ni"], it["t"] + it["lead"], it["d"]) for it in items if it["kind"] == "N"]
NS = sum(d for _, _, d in nar); DS = sum(it["d"] for it in items if it["kind"] == "D")   # 대사 창 화면 초
srcuse = sum(min(y, SRCLEN) - x for z in used for x, y in used[z])
rep = [f"화면 {mm(BODY)} ({BODY:.0f}초) · 원본 {SRCLEN / 60:.0f}분의 {100 * BODY / SRCLEN:.0f}% · 나레 {len(nar)}줄 {NS:.0f}초 = {100 * NS / BODY:.0f}% · 대사 창 {sum(1 for it in items if it['kind'] == 'D')}개 {DS:.0f}초 · 조각 {len(W)} · 원본 쓴 양 {srcuse / 60:.1f}분",
       f"가장 긴 조각 {max(w['b'] - w['a'] for w in W):.2f}초 · 대사 창 최장 {max([it['d'] for it in items if it['kind'] == 'D'] or [0]):.2f}초"]
_tl = [it["tail"] / DSPD for it in items if it.get("tail")]
if DTAIL > 0 or SCPAD > 0: rep.append(f"대사 여운 {len(_tl)}곳(평균 {sum(_tl) / max(1, len(_tl)):.2f}초) · 장면 바뀜 숨 {sum(1 for it in items if it.get('scene_end'))}곳")
rep.append(("옛 방식(legacy_spread)" if LEGACY else f"11-07 규칙: 나레 구간 {NSPAN:g}초 안 · 다음 대사에서 자름 · 되감기 {REWIND:g}초") + f" · 글자 조각 반전 안 함 {ntx}" + ("" if TS else " (text_scan.json 없음 — prep/textflip.py)"))
rep += [f"△ {x}" for x in WARN]
rep += [f"✗ {p}" for p in problems]
open("plan_report.txt", "w", encoding="utf-8").write("\n".join(rep) + "\n")
print("\n".join(rep[:3]))
for x in WARN: print("  △", x)
print(f"문제 {len(problems)}")
for p in problems[:60]: print("  ✗", p)
if not DRY:
    json.dump(W, open("windows.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump([{"ni": n, "t": round(t, 3), "d": round(d, 3)} for n, t, d in nar], open("narr_place.json", "w"), indent=0)
else:
    json.dump(W, open("windows_dry.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
sys.exit(1 if problems else 0)
