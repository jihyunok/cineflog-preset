# -*- coding: utf-8 -*-
"""굽기 전 관문 (10-13 사용자 "왜 한번에 못잡아? 처음부터 그렇게 세팅을하지말아야지" / "핀치하나 만드는데 3일걸렸어").
하나라도 걸리면 exit 1 — build_v9 는 그때 굽지 않는다. 16 핀치에서 사용자가 하나씩 찾아낸 것들을 굽기 전에 전부 잰다.
 pre  (자르기 전): ① 나레 조각 토막·경계(gem_split v2 잣대) ② 나레 겹침 ③ 화면 시간 끊김 ④ 멈춤(hold)·느리게(rate<0.85) ⑤ 0.5초 깜빡 조각
                   ⑥ 원본 3초 간격(구역별) ⑦ 대사 창 가장자리 말 잘림(v9/edges) ⑧ 까만 화면(black_src.npy, 0.75초+) ⑨ 나레↔그림(제브, 있으면)
                   ⑫ 원본 3초(ep.json max_piece) 넘게 이어 쓴 조각(대사 창 포함, 10-14 소유권 주장) ⑬ ep.json min_total 아래(10-20부터 기본 없음)
                   ⑭ 첫 사건({"event": True} 줄)이 완성본 3분 안 ⑮ 앞 5분에 나레 없이 대사만 5줄 넘게(10-20 앞 3분 이탈 50%+)
                   ⑯ 훅 첫 10초 사람 확인(hook_check.json — prep/hookcheck.py 시트를 보고 조각마다 본 것·ok, 나레가 말한 장면 key_scene_shown)
                   ⑰ 반전 조각 글자 검사(text_scan.json — prep/textflip.py · 검사 안 된 반전 조각 · 글자 구간과 겹치는 반전 조각)
 final(굽기 직전): ⑩ 나레 자막 ↔ 목소리(subcheck4 잣대: 자막 빠름·늦음 0.4초, 목소리에 자막 빔 0.6초) ⑪ 자막 두 줄 겹침
사용: python gate.py pre  /  python gate.py final subs.ass narr_track.wav
예외: gate_allow.json — 눈으로 확인한 가짜만, 이유를 SESSION-LOG 에 남긴다.
  ["검사 문구 일부", …](옛 꼴) 또는 {"검사 문구 일부": "이유" | {"seen": "그 시각 프레임에 보이는 것", …}}
  ★11-07 (33 콜래트럴: ⑨ 38조각을 같은 문구 「눈으로 봄」으로 일괄 허용 · 확인 시트는 IndexError 로 실패해 있었음)
   - ⑧⑨⑰(그림 검사)는 {"seen": 12자+} 만 허용 — 문자열·옛 꼴은 거절 「(허용 거절: 본 것 없음)」
   - 같은 이유 글이 2건 이상 되풀이되면 그 건 전부 거절
   - ⑨ 는 _npsheet_ok.json(prep/npsheet.py 가 시트를 다 만든 뒤 씀)의 win_sig 가 지금 windows.json 과 같고 그 조각 id 가 ids 에 있어야 — 아니면 ⑨ 허용 0
   - ⑯ 과 ⑰ 「없음·검사 안 됨」은 허용 안 됨(도구를 돌리고 사람이 채울 것) — ⑰ 「글자 조각 반전」만 조각마다 seen 으로 허용"""
import hashlib, json, os, re, subprocess, sys
from collections import Counter
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "gemini_tts"))
import hooksig as HS
MODE = sys.argv[1]
_RAW = json.load(open("gate_allow.json", encoding="utf-8")) if os.path.exists("gate_allow.json") else []
ALLOW = {str(a): "" for a in _RAW} if isinstance(_RAW, list) else dict(_RAW)
def _why(v): return (v.get("seen") or "").strip() if isinstance(v, dict) else str(v or "").strip()
_NW = Counter(_why(v) for v in ALLOW.values() if _why(v))
DUPW = {t for t, n in _NW.items() if n >= 2}          # ★11-07 같은 문구 되풀이 = 보지 않고 쓴 것 → 전부 거절
for t in DUPW: print(f"  허용 거절: 같은 문구 {_NW[t]}건 반복 — 「{t[:60]}」")
def _sha1(p): return hashlib.sha1(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None
_NPOK = json.load(open("_npsheet_ok.json", encoding="utf-8")) if os.path.exists("_npsheet_ok.json") else {}
NP_IDS = set(_NPOK.get("ids") or []) if _NPOK.get("win_sig") and _NPOK["win_sig"] == _sha1("windows.json") else None
VIS = ("⑧", "⑨", "⑰")
_said = set()
def _ok(v, what):
    t = _why(v)
    if what.startswith(VIS) and (not isinstance(v, dict) or len(t) < 12): return "본 것 없음"
    if t in DUPW: return "같은 문구 반복"
    if what.startswith("⑨"):
        if NP_IDS is None:
            if "np" not in _said: _said.add("np"); print("  허용 거절: 확인 시트 없음/낡음 — ⑨ 허용 0")
            return "확인 시트 없음/낡음"
        m = re.search(r"n\d{3}_w\d+_-?\d+\.\d", what)
        if not m or m.group(0) not in NP_IDS: return "확인 시트에 없는 조각"
    return None
bad = []
def fail(what, allow=True):
    why = []
    for a, v in (ALLOW.items() if allow else ()):
        if not a or a not in what: continue
        r = _ok(v, what)
        if r is None: print("  (허용)", what, "—", _why(v)[:60]); return
        why.append(r)
    if why: print(f"  (허용 거절: {why[0]})", what)
    bad.append(what)
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"

if MODE == "pre":
    import edges as EDG, gem_split as GS
    CFG = json.load(open("ep.json", encoding="utf-8")); SPD, GAP = 1.05, 3.0
    TAIL0, TGAP = (CFG.get("tail_src") or [1e18])[0], CFG.get("tail_gap", GAP)     # 10-31 plan_v9 와 같게(꼬리 구간만 간격 따로)
    WN = json.load(open("windows.json", encoding="utf-8")); PL = json.load(open("narr_place.json"))
    # ① 나레 조각
    srcdb = {}
    for q in PL:
        w = f"narr/n{q['ni']:03d}.wav"; j = json.load(open(f"narr/n{q['ni']:03d}.json", encoding="utf-8"))
        for y in GS.check_piece(w, j["text"]):
            if y.startswith(("앞 토막", "끝 토막")) and not GS.frag_ok(w, j["text"], [y]): continue
            fail(f"① 나레 n{q['ni']:03d} {y}")
        src = j.get("src")
        if src and os.path.exists(src[0]):
            if src[0] not in srcdb: db = GS.env_db(GS.load16(src[0])); srcdb[src[0]] = (db, GS.gaps(db))
            db, gp = srcdb[src[0]]
            for e in (src[1], src[2]):
                if e < 0.05 or e > len(db) * GS.HOP - 0.05: continue
                c, r = GS.refine(e, db, gp, "")
                if abs(c - e) > 0.03 and r != "R3" and not r.startswith("R1"): fail(f"① 나레 n{q['ni']:03d} 경계 {e:.2f} 소리 토막 옆({r})")
    # ② 나레 겹침
    P = sorted(PL, key=lambda q: q["t"])
    for x, y in zip(P, P[1:]):
        if x["t"] + x["d"] > y["t"] - 0.05: fail(f"② 나레 겹침 n{x['ni']:03d}→n{y['ni']:03d} {mm(y['t'])}")
    # ③④⑤
    for i in range(len(WN) - 1):
        if abs(WN[i]["b"] - WN[i + 1]["a"]) > 0.005: fail(f"③ 화면 시간 끊김 {mm(WN[i]['b'])}")
    for w in WN:
        if w.get("hold", 0) > 0.005: fail(f"④ 멈춤 {mm(w['a'])} {w['hold']}초")
        if w.get("rate", 1.05) < 0.85: fail(f"④ 느리게 {mm(w['a'])} {w['rate']}")
        if w["b"] - w["a"] < 0.5: fail(f"⑤ 깜빡 조각 {mm(w['a'])} {w['b'] - w['a']:.2f}초")
    # ⑥ 3초 간격
    def slen(w): return (w["b"] - w["a"]) * w.get("rate", SPD if w["kind"] == "A" else 1)     # D 창 rate·pre = drate.py(10-14)
    def s0(w): return w["s"] - w.get("pre", 0)
    # ⑫ 원본을 3초 넘게 이어 쓴 조각 (10-14 17 그레이하운드 v10 도 Apple IPE 소유권 주장 — 대사 창 최장 5.9초·63% → 사용자 "1" 대사 창 3초 이하)
    # ⑬ 완성 길이 20분 아래 (10-14 사용자 "14분으로 줄이면 뭐가 재밌니" / "너 앞으로 영화리뷰할때 20아래로만들지마") — 몸통 + 끝 1.5초(끝 검은 화면 15초는 10-14 뺌)
    tot = WN[-1]["b"] + CFG.get("tail", 1.5)
    # ★10-17 "25분이상좀만들어줘" → ★10-20 폐지: 사용자 "시간은 지킬필요가 없어"(앞 3분 이탈 50%+ — 길이 채우려 넣은 일상 대사 토막이 원인). ep.json min_total 을 적은 편만 잰다
    if tot < CFG.get("min_total", 0): fail(f"⑬ 완성 {mm(tot)} — ep.json min_total {CFG['min_total']}초 아래")
    MAXP = CFG.get("max_piece", 3.0)   # ★10-20 애플·아마존 3초 · 그 밖은 ep.json max_piece 6 까지(강의: 원본 소리 6초 이하)
    for w in WN:
        if w["b"] - w["a"] > MAXP + 0.01 or slen(w) > MAXP * SPD + 0.02: fail(f"⑫ {w['kind']} 조각 {mm(w['a'])} 화면 {w['b'] - w['a']:.2f}초·원본 {slen(w):.2f}초 — {MAXP:g}초 넘음(대사는 나레로 바꾸거나 한쪽 말만)")
    # ⑭ 첫 사건 3분 안 · ⑮ 앞 5분 대사 토막 줄줄이 (10-20 사용자 "3분이내에이탈율이 50프로가 넘고 … 앞 장면이재미있지않다는거지" / "몰입도 있게 영상을 못끌고")
    #   대본에서 첫 사건(싸움·반전·사고·누명) 줄에 {"event": True} — 훅 뒤 본편에서 완성본 180초 안에 와야 한다
    #   쇼츠(ep.json "shorts": true — shorts/shorts_setup.py 가 적음)는 한 사건 1:40~2:30 이라 ⑭⑮ 를 안 잰다
    ev = [w["a"] for w in WN if w.get("event") and w.get("z", "main") != "hook"]
    if CFG.get("shorts"): pass
    elif not ev: fail("⑭ 첫 사건 표시 없음 — 대본의 첫 사건 줄에 {\"event\": True}")
    elif min(ev) > CFG.get("event_by", 180): fail(f"⑭ 첫 사건 {mm(min(ev))} — 3분 넘음(인물 소개·일상은 나레 한두 줄로 넘길 것)")
    #   ⑮ 나레 없이 대사 창(D 줄)만 5줄 넘게 이어지면 실패 — 사이에 나레가 한 번이라도 시작하면 끊긴 것으로 본다
    NT = sorted(q["t"] for q in PL)
    DW = [] if CFG.get("shorts") else sorted({w["k"]: w for w in WN if w["kind"] == "D" and w["a"] < 300}.values(), key=lambda w: w["a"])
    run = []
    for w in DW:
        if run and any(run[-1]["b"] - 0.05 <= t < w["a"] for t in NT): run = []
        run.append(w)
        if len(run) == 5: fail(f"⑮ 앞 5분 {mm(run[0]['a'])}~ 나레 없이 대사만 5줄 넘게 — 일상 대사 토막은 나레 한 줄로")
    for z in sorted({w.get("z", "main") for w in WN}):
        sp = sorted((s0(w), s0(w) + slen(w), w["a"], bool(w.get("cont"))) for w in WN if w.get("z", "main") == z)
        for x, y in zip(sp, sp[1:]):
            # ★11-03 핵심 장면 이음({"cont": True} 나레 조각) — 앞 대사 → 이음 나레 → 다음 대사는 한 장면으로 이어 붙이는 것(plan_v9 LINKS), 겹침만 아니면 통과
            if (x[3] or y[3]) and -0.05 <= y[0] - x[1] <= 3.05: continue
            if y[0] - x[1] < (TGAP if min(x[0], y[0]) >= TAIL0 - 1e-6 else GAP) - 0.01: fail(f"⑥ {z} 원본 3초 간격 {mm(x[2])}/{mm(y[2])} ({y[0] - x[1]:.2f}초)")
    # ⑦ 대사 가장자리
    env = EDG.Env(CFG["src"], CFG.get("words", "src_words.json"), cache=CFG.get("band", "src_band.npy"))
    for i, t, side, why in EDG.check(WN, env): fail(f"⑦ 대사 {mm(t)} {'시작' if side == 's' else '끝'} 말 잘림: {why}")
    # ⑧ 까만 화면
    if os.path.exists("black_src.npy"):
        B = np.load("black_src.npy") < 0.08
        for w in WN:
            k0 = int(s0(w) * 4); k1 = int((s0(w) + slen(w)) * 4) + 1; sec = B[k0:k1].sum() / 4
            if sec >= 0.75: fail(f"⑧ 까만 화면 {mm(w['a'])} 원본 {mm(w['s'])} {sec:.2f}초")
    # ⑨ 나레↔그림 (제브 판정 결과 jev_np_out.jsonl 이 있으면: contradicts ≥ 0.6 이고 shows_narrated < 0.3)
    if os.path.exists("jev_np_out.jsonl"):
        for l in open("jev_np_out.jsonl", encoding="utf-8"):
            j = json.loads(l); a = j["answers"]
            if a["contradicts"] >= 0.6 and a["shows_narrated"] < 0.3: fail(f"⑨ 나레↔그림 어긋남 {j['id']} (어긋남 {a['contradicts']:.2f}, 맞음 {a['shows_narrated']:.2f})")
    else: print("  ⑨ 나레↔그림 판정 파일 없음(jev_np_out.jsonl) — narr_pic.py 먼저")
    # ⑯ 훅 첫 10초 사람 확인 (★11-07 33 콜래트럴: 훅 「택시 위로 남자가 떨어집니다」에 택시도 추락도 안 나옴) — 허용 안 됨
    HW = HS.hook_windows(WN)
    if CFG.get("shorts") or not (any(w.get("z") == "hook" for w in WN) or any(q["t"] < HS.HOOK_SEC for q in PL)): pass
    elif not os.path.exists("hook_check.json"): fail("⑯ hook_check.json 없음 — prep/hookcheck.py 로 앞 10초 시트를 만들고 눈으로 보고 채울 것", False)
    else:
        HC = json.load(open("hook_check.json", encoding="utf-8")); P16 = HC.get("pieces") or []
        if HC.get("win_sig") != HS.sig(WN): fail("⑯ hook_check.json 낡음(앞 10초 조각이 바뀜) — prep/hookcheck.py 다시 · 다시 보고 채울 것", False)
        else:
            if len(P16) != len(HW): fail(f"⑯ hook_check.json 조각 {len(P16)}개 ≠ 앞 10초 조각 {len(HW)}개 — prep/hookcheck.py 다시", False)
            for p in P16:
                sn = (p.get("seen") or "").strip()
                if len(sn) < 8: fail(f"⑯ 훅 조각 w{p.get('w')} {mm(p.get('a', 0))} 본 것 안 적음(8자+)", False)
                elif p.get("ok") is not True: fail(f"⑯ 훅 조각 w{p.get('w')} {mm(p.get('a', 0))} ok 아님 「{sn[:30]}」", False)
            for t, n in Counter((p.get("seen") or "").strip() for p in P16 if (p.get("seen") or "").strip()).items():
                if n >= 2: fail(f"⑯ 훅 본 것 같은 문구 {n}건 반복 「{t[:30]}」 — 조각마다 그 프레임에 보이는 것을 따로", False)
            if HC.get("key_scene_shown") is not True: fail(f"⑯ 나레가 말한 장면이 앞 10초에 안 나옴/확인 안 함(key_scene_shown) 「{(HC.get('key_scene') or '')[:30]}」", False)
    # ⑰ 반전 조각 글자 검사 (★11-07 33 콜래트럴: 택시 지붕 「IXAT」 등 글자 컷 7곳 반전) — text_scan.json(prep/textflip.py)
    FL = [w for w in WN if not w.get("noflip")]
    if not os.path.exists("text_scan.json"): fail("⑰ text_scan.json 없음 — prep/textflip.py 로 글자 조각 검사", False)
    else:
        TS = json.load(open("text_scan.json", encoding="utf-8")); SC = [(float(r[0]), float(r[1])) for r in TS.get("scanned", [])]
        TX = [(float(r[0]), float(r[1]), str(r[2]) if len(r) > 2 else "") for r in TS.get("text", []) + TS.get("manual", [])]
        un = [w for w in FL if not any(a - 0.3 <= s0(w) + slen(w) / 2 <= b + 0.3 for a, b in SC)]
        if un: fail(f"⑰ 반전 조각 {len(un)}개 글자 검사 안 됨(화면 {', '.join(mm(w['a']) for w in un[:5])}{' …' if len(un) > 5 else ''}) — prep/textflip.py 다시", False)
        for w in FL:
            hit = [x for x in TX if s0(w) < x[1] and s0(w) + slen(w) > x[0]]
            if hit: fail(f"⑰ 글자 조각 반전 {mm(w['a'])} 원본 {mm(s0(w))} 「{hit[0][2][:30]}」 — noflip(plan_v9 다시)")
else:
    ASS, V = sys.argv[2], sys.argv[3]
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", V, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(b, np.float32); F = 160
    on = np.sqrt(np.mean(x[:len(x) // F * F].reshape(-1, F) ** 2, 1)) > 0.02; k = 0
    while k < len(on):
        if not on[k]:
            j = k
            while j < len(on) and not on[j]: j += 1
            if j - k < 15 and k > 0: on[k:j] = True
            k = j
        else: k += 1
    def ts(s):
        h, m, c = s.split(":"); return int(h) * 3600 + int(m) * 60 + float(c)
    rows = [(ts(l.split(",")[1]), ts(l.split(",")[2]), l.split(",")[3], l.rstrip("\n").split(",", 9)[9]) for l in open(ASS, encoding="utf-8") if l.startswith("Dialogue") and ",TOP," not in l and ",TAG," not in l]   # 10-20 인물 이름표(TAG)는 자막이 아님
    L = sorted((a, z, t) for a, z, st, t in rows if st in ("N", "NP", "NE"))   # ★10-16 지무비식 자막: 나레 꼴 NP(일반)·NE(강조)도 나레
    def fr(t): return min(max(int(t * 100), 0), len(on) - 1)
    for i, (a, z, t) in enumerate(L):
        if not on[fr(a)]:
            j = fr(a)
            while j < len(on) and not on[j]: j += 1
            if j / 100 - a > 0.4 and j / 100 < z: fail(f"⑩ 나레 자막 빠름 {mm(a)} {j / 100 - a:.2f}초 「{t}」")
        else:
            j = fr(a)
            while j > 0 and on[j - 1]: j -= 1
            prev_end = L[i - 1][1] if i else 0
            if a - j / 100 > 0.4 and j / 100 >= prev_end - 0.05: fail(f"⑩ 나레 자막 늦음 {mm(a)} {a - j / 100:.2f}초 「{t}」")
    cov = np.zeros(len(on), bool)
    for a, z, _ in L: cov[fr(a):fr(z)] = True
    k = 0
    while k < len(on):
        if on[k] and not cov[k]:
            j = k
            while j < len(on) and on[j] and not cov[j]: j += 1
            if j - k > 60: fail(f"⑩ 목소리에 자막 빔 {mm(k / 100)} {(j - k) / 100:.2f}초")
            k = j
        else: k += 1
    A = sorted((a, z) for a, z, st, t in rows)
    for (a1, z1), (a2, z2) in zip(A, A[1:]):
        if z1 > a2 + 0.01: fail(f"⑪ 자막 두 줄 겹침 {mm(a2)}")
print(f"관문 {MODE}: 문제 {len(bad)}")
for x in bad[:80]: print("  ✗", x)
sys.exit(1 if bad else 0)
