# -*- coding: utf-8 -*-
"""굽기 전 관문 (10-13 사용자 "왜 한번에 못잡아? 처음부터 그렇게 세팅을하지말아야지" / "핀치하나 만드는데 3일걸렸어").
하나라도 걸리면 exit 1 — build_v9 는 그때 굽지 않는다. 16 핀치에서 사용자가 하나씩 찾아낸 것들을 굽기 전에 전부 잰다.
 pre  (자르기 전): ① 나레 조각 토막·경계(gem_split v2 잣대) ② 나레 겹침 ③ 화면 시간 끊김 ④ 멈춤(hold)·느리게(rate<0.85) ⑤ 0.5초 깜빡 조각
                   ⑥ 원본 3초 간격(구역별) ⑦ 대사 창 가장자리 말 잘림(v9/edges) ⑧ 까만 화면(black_src.npy, 0.75초+) ⑨ 나레↔그림(제브, 있으면)
                   ⑫ 원본 3초(ep.json max_piece) 넘게 이어 쓴 조각(대사 창 포함, 10-14 소유권 주장) ⑬ ep.json min_total 아래(10-20부터 기본 없음)
                   ⑭ 첫 사건({"event": True} 줄)이 완성본 3분 안 ⑮ 앞 5분에 나레 없이 대사만 5줄 넘게(10-20 앞 3분 이탈 50%+)
 final(굽기 직전): ⑩ 나레 자막 ↔ 목소리(subcheck4 잣대: 자막 빠름·늦음 0.4초, 목소리에 자막 빔 0.6초) ⑪ 자막 두 줄 겹침
사용: python gate.py pre  /  python gate.py final subs.ass narr_track.wav
예외: gate_allow.json ["검사 문구 일부", …] — 눈으로 확인한 가짜만, 이유를 SESSION-LOG 에 남긴다."""
import json, os, re, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "gemini_tts"))
MODE = sys.argv[1]
ALLOW = json.load(open("gate_allow.json", encoding="utf-8")) if os.path.exists("gate_allow.json") else []
bad = []
def fail(what):
    if any(a in what for a in ALLOW): print("  (허용)", what); return
    bad.append(what)
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"

if MODE == "pre":
    import edges as EDG, gem_split as GS
    CFG = json.load(open("ep.json", encoding="utf-8")); SPD, GAP = 1.05, 3.0
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
        sp = sorted((s0(w), s0(w) + slen(w), w["a"]) for w in WN if w.get("z", "main") == z)
        for x, y in zip(sp, sp[1:]):
            if y[0] - x[1] < GAP - 0.01: fail(f"⑥ {z} 원본 3초 간격 {mm(x[2])}/{mm(y[2])} ({y[0] - x[1]:.2f}초)")
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
