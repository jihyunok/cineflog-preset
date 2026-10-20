# -*- coding: utf-8 -*-
"""AI 스튜디오(Gemini 3.8 Flash TTS)에서 나레 여러 조각을 한 번에 뽑은 wav 를 조각별로 자른다.
결과: <out>/nNNN.wav(-16 LUFS, 48k 스테레오) + nNNN.json(chars/st/en/src — build 자막 타이밍용)
사용: python gem_split.py 배치.wav 시작ni 끝ni [--out narr] [--asr sm|groq] [--items items.json]

10-13 v2 (사용자 "왜 한번에 못잡아? 처음부터 그렇게 세팅을하지말아야지"):
16 핀치에서 Groq 낱말 끝 시각(0.1~0.3초 이름)에서 잘라 「있었고」의 「고」가 다음 조각 맨 앞에, 「그곳까지」의 「그」가 앞 조각 끝에 따로 붙었다.
그걸 뒤에서 narr_recut.py 로 따로 고쳤다 → 이제 자르는 이 도구 안에서 처음부터:
 1. 받아쓰기는 Speechmatics(기본, 사용자 "스피치매틱스로하는거 맞지?"). --asr groq 는 손으로 고를 때만.
 2. 대본 글자 ↔ 받아쓴 글자를 맞대어 경계 근처를 찾고, 마지막 자리는 원본 wav 소리 크기(10ms)로 정한다(narr_recut 규칙):
    R3 0.2초+ 쉼 안이면 그 쉼 가운데 · R1 경계 뒤 0.35초 안 짧은 토막이 쉼으로 끝나면 그 토막은 앞 문장 꼬리 → 그 뒤 쉼 가운데
    R2 경계 앞 0.15초 안 토막이 쉼 뒤에 있으면 다음 문장 머리 → 그 앞 쉼 가운데 · R4 소리 속이면 ±0.12초 안 가장 조용한 곳
 3. 앞뒤 쉼 깎기도 소리 크기로 직접(-45dB) → 깎은 만큼 글자 시각을 정확히 당긴다.
 4. 글자 시각은 대본 글자 ↔ 받아쓴 글자 짝짓기(옛 realign.py 방식)로 바로 → 따로 realign 안 돌려도 된다.
 5. 다 자른 뒤 스스로 검사 — ★경계를 소리 크기 규칙으로 다시 재서 옮길 데가 남으면 실패(받아쓰기는 「고」 같은 한 글자 토막을 못 듣는다, 16 핀치 실측) + 조각 앞뒤 떨어진 토막·경계가 소리 속(−30dB 넘음)·길이가 글자 수에 안 맞음·받아쓰기 짝 50% 안 → 하나라도 있으면 exit 1(목록 출력)."""
import difflib, json, os, re, subprocess, sys, time, uuid, urllib.request, urllib.error
import numpy as np
SR = 16000; HOP = 0.01; SIL = -40.0; TRIM = -45.0

def batch_ids(n0, n1):
    """묶음의 줄 번호 — batches.json 4번째 칸(10-19, 떨어진 줄도 한 묶음)이 있으면 그 순서, 없으면 n0~n1"""
    B = json.load(open("batches.json", encoding="utf-8")) if os.path.exists("batches.json") else []
    return next((b[3] for b in B if len(b) > 3 and b[0] == n0 and b[1] == n1), None) or list(range(n0, n1 + 1))
def arg(k, d=None):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
def norm(s): return re.sub(r"[^0-9A-Za-z가-힣]", "", s)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
def load16(p, ss=None, to=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", f"{ss:.3f}"] if ss is not None else []) + (["-to", f"{to:.3f}"] if to is not None else []) + ["-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)
def env_db(x):
    n = int(HOP * SR); m = len(x) // n
    return 20 * np.log10(np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(1) + 1e-12))
def runs(db, thr=SIL):
    """[(조용한가, 시작초, 끝초)] — 10ms 칸"""
    s = db < thr; out = []; k = 0
    while k < len(s):
        j = k
        while j < len(s) and s[j] == s[k]: j += 1
        out.append((bool(s[k]), round(k * HOP, 2), round(j * HOP, 2))); k = j
    return out
def gaps(db, thr=SIL, mind=0.08): return [(a, b) for q, a, b in runs(db, thr) if q and b - a >= mind]

# ── 받아쓰기
def asr_groq(mp3):
    key = open(os.path.expanduser("~/.volcano/keys/groq"), encoding="utf-8").read().strip()
    b = "----x" + uuid.uuid4().hex; parts = []
    for k, v in [("model", "whisper-large-v3"), ("response_format", "verbose_json"), ("temperature", "0"), ("language", "ko"), ("timestamp_granularities[]", "word")]:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode()); parts.append(open(mp3, "rb").read()); parts.append(f"\r\n--{b}--\r\n".encode())
    while True:
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=b"".join(parts), headers={"Authorization": "Bearer " + key, "Content-Type": "multipart/form-data; boundary=" + b, "User-Agent": "curl/8"}), timeout=300)).get("words", [])
        except urllib.error.HTTPError as e:
            print("  ", e.code, e.read().decode()[:200], flush=True)
            if e.code == 429: time.sleep(40); continue
            if e.code >= 500: time.sleep(10); continue
            raise
def asr_sm(mp3, lang="ko"):
    """Speechmatics 배치 → [{word,start,end}] (문장부호 빼고)"""
    key = (os.environ.get("SPEECHMATICS_API_KEY") or open(os.path.expanduser("~/.volcano/keys/speechmatics"), encoding="utf-8").read()).strip()
    API = "https://asr.api.speechmatics.com/v2"; H = {"Authorization": "Bearer " + key}
    def get(url):
        for k in range(10):
            try: return urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=180).read().decode()
            except Exception as e:
                if k == 9: raise
                time.sleep(10 + 5 * k)
    cfg = json.dumps({"type": "transcription", "transcription_config": {"language": lang, "operating_point": "enhanced"}})
    b = "----sm" + uuid.uuid4().hex
    body = b"".join([f"--{b}\r\nContent-Disposition: form-data; name=\"config\"\r\n\r\n{cfg}\r\n".encode(),
                     f"--{b}\r\nContent-Disposition: form-data; name=\"data_file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode(), open(mp3, "rb").read(), f"\r\n--{b}--\r\n".encode()])
    for k in range(5):
        try:
            jid = json.loads(urllib.request.urlopen(urllib.request.Request(API + "/jobs", data=body, headers={**H, "Content-Type": "multipart/form-data; boundary=" + b}), timeout=600).read().decode())["id"]; break
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:300]
            if e.code in (429, 500, 502, 503) and k < 4: time.sleep(15); continue
            sys.exit(f"Speechmatics 접수 실패 {e.code} {msg}")
    while True:
        st = json.loads(get(f"{API}/jobs/{jid}"))["job"]["status"]
        if st != "running": break
        time.sleep(5)
    if st != "done": sys.exit(f"Speechmatics 실패 {jid} {st}")
    t = json.loads(get(f"{API}/jobs/{jid}/transcript?format=json-v2"))
    return [{"word": (it.get("alternatives") or [{}])[0].get("content", ""), "start": it["start_time"], "end": it["end_time"]} for it in t.get("results", []) if it["type"] == "word"]

def words_of(wav, how):
    """배치 wav 전체 낱말 시각(캐시 <wav>_words_<how>.json)"""
    cj = wav[:-4] + f"_words_{how}.json"
    if os.path.exists(cj): return json.load(open(cj, encoding="utf-8"))
    D = dur(wav); allw = []
    if how == "sm":
        mp3 = wav[:-4] + "_sm.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-ac", "1", "-ar", "16000", "-b:a", "64k", mp3], check=True)
        allw = asr_sm(mp3); os.remove(mp3)
    else:                                   # Groq 는 긴 파일 뒤쪽이 꼬여 약 50초 토막으로(b007)
        gp = gaps(env_db(load16(wav)), mind=0.18); cuts = [0.0]
        while D - cuts[-1] > 70:
            want = cuts[-1] + 50; g = min(gp, key=lambda g: abs((g[0] + g[1]) / 2 - want) if (g[0] + g[1]) / 2 > cuts[-1] + 20 else 1e9)
            cuts.append((g[0] + g[1]) / 2)
        cuts.append(D)
        for i in range(len(cuts) - 1):
            mp3 = wav[:-4] + f"_g{i}.mp3"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{cuts[i]:.3f}", "-to", f"{cuts[i+1]:.3f}", "-i", wav, "-ac", "1", "-ar", "16000", "-b:a", "64k", mp3], check=True)
            allw += [{"start": w["start"] + cuts[i], "end": w["end"] + cuts[i], "word": w["word"]} for w in asr_groq(mp3)]; os.remove(mp3)
    json.dump(allw, open(cj, "w", encoding="utf-8"), ensure_ascii=False)
    return allw

# ── 경계 다듬기 (narr_recut 규칙)
def short_lead(text):                       # 「그때,」「결국」처럼 짧은 낱말 + 쉼표/끝
    return bool(re.match(r"\s*(\S{1,3}?)[,.]", text)) or len(norm(text)) <= 3
def refine(t, db, gp, next_text):
    LG = [g for g in gp if g[1] - g[0] >= 0.2]
    gin = next((g for g in gp if g[0] - 0.005 <= t <= g[1] + 0.005), None)
    if gin and gin[1] - gin[0] >= 0.2: return (gin[0] + gin[1]) / 2, "R3"
    st = gin[1] if gin else t; en = gin[0] if gin else t
    nx = min((g for g in LG if g[0] >= st - 0.005), key=lambda g: g[0], default=None)
    pv = max((g for g in LG if g[1] <= en + 0.005), key=lambda g: g[1], default=None)
    b1 = nx[0] - st if nx else 9; b2 = en - pv[1] if pv else 9
    c1 = b1 < (0.15 if short_lead(next_text) else 0.35); c2 = b2 < 0.15
    if c1 and (not c2 or b1 <= b2): return (nx[0] + nx[1]) / 2, f"R1 뒤 토막 {b1:.2f}"
    if c2: return (pv[0] + pv[1]) / 2, f"R2 앞 토막 {b2:.2f}"
    k = int(round(t / HOP))
    if db[max(0, k - 1):k + 2].max() > SIL:
        lo, hi = max(1, k - 12), min(len(db) - 2, k + 12); sm = np.convolve(db, np.ones(3) / 3, "same")
        q = lo + int(np.argmin(sm[lo:hi + 1]))
        if sm[q] < sm[k] - 1: return q * HOP, f"R4 조용한 곳 {sm[k]:.0f}→{sm[q]:.0f}dB"
    return t, "그대로"

def split(wav, texts, W, db):
    """texts = [(ni, text)] 순서대로. 반환: 조각별 (a, b) 초, 경계 기록"""
    D = len(db) * HOP; gp = gaps(db)
    W = [(w["start"], w["end"], norm(w["word"])) for w in W]; W = [w for w in W if w[2]]
    M = []                                   # 시각이 거꾸로 가는(받아쓰기 헛소리) 단어는 버린다
    for w in W:
        if not M or (w[0] >= M[-1][0] - 0.05 and w[1] >= w[0]): M.append(w)
    W = M
    A = ""; owner = []
    for k, w in enumerate(W): A += w[2]; owner += [k] * len(w[2])
    T = ""; ends = []
    for _, t in texts: T += norm(t); ends.append(len(T))
    sm = difflib.SequenceMatcher(None, T, A, autojunk=False); m = {}
    for a0, b0, n in sm.get_matching_blocks():
        for j in range(n): m[a0 + j] = b0 + j
    def asr_pos(i):
        lo = next((m[x] for x in range(i, -1, -1) if x in m), 0); hi = next((m[x] for x in range(i, len(T)) if x in m), len(A) - 1)
        return lo if i in m else (lo + hi) / 2
    bounds = []; log = []
    for q, e in enumerate(ends[:-1]):
        p = asr_pos(e - 1); k = owner[min(len(owner) - 1, int(round(p)))]
        tb = W[k][1]; nb = W[k + 1][0] if k + 1 < len(W) else D
        k2 = owner[min(len(owner) - 1, int(round(asr_pos(e))))]
        if k2 == k:                          # 두 조각 글자가 한 낱말로 묶임 → 글자 비율 자리(뒤에서 소리 크기로 다듬음)
            ci = [i for i, o in enumerate(owner) if o == k]; r = (int(round(p)) - ci[0] + 1) / len(ci)
            tb = nb = W[k][0] + (W[k][1] - W[k][0]) * r
        cand = [(a, b) for a, b in gp if b > tb - 0.15 and a < nb + 0.15]
        cut = (lambda g: (max(g[0], tb - 0.15) + min(g[1], nb + 0.15)) / 2)(max(cand, key=lambda g: g[1] - g[0])) if cand else (tb + nb) / 2
        c2, rule = refine(cut, db, gp, texts[q + 1][1])
        bounds.append(c2); log.append((texts[q][0], round(cut, 2), round(c2, 2), rule))
    for i in range(1, len(bounds)):          # 경계는 앞으로만 — 최소 길이는 글자 수로(「결국」 두 글자 0.18초: 16 핀치 n117 은 0.8초 고정 때문에 뒤 경계가 소리 속으로 밀렸다)
        mn = max(0.15, 0.06 * len(norm(texts[i][1])))
        if bounds[i] < bounds[i - 1] + mn:
            bounds[i], r = refine(bounds[i - 1] + mn, db, gp, texts[i + 1][1]); log.append((texts[i][0], "밀림", round(bounds[i], 2), r))
    edges = [0.0] + bounds + [D]
    return [(edges[i], edges[i + 1]) for i in range(len(texts))], W, log

def trim(db, a, b):
    """[a,b] 안 실제 소리 시작·끝(−45dB, 0.05초 넘게 이어진 소리만 — 딸깍·숨 같은 0.01~0.04초 잡음은 소리로 안 침) — 앞 0.02·뒤 0.06초 여유"""
    i0, i1 = int(a / HOP), int(b / HOP); on = db[i0:i1] > TRIM; R = []; k = 0
    while k < len(on):
        j = k
        while j < len(on) and on[j] == on[k]: j += 1
        if on[k] and j - k >= 5: R.append((k, j))
        k = j
    if not R: return a, b
    return max(a, (i0 + R[0][0]) * HOP - 0.02), min(b, (i0 + R[-1][1]) * HOP + 0.06)

def char_times(text, a, W):
    """대본 글자 ↔ 받아쓴 글자 짝짓기(옛 realign.py) — 조각 시작 a 기준 초. 짝 없는 글자는 앞뒤 사이로"""
    ws = [w for w in W if w[0] >= a - 0.3]
    C = []; CT = []
    for w0, w1, t in ws:
        for k, c in enumerate(t): C.append(c); CT.append((w0 + (w1 - w0) * k / len(t) - a, w0 + (w1 - w0) * (k + 1) / len(t) - a))
    S = [(k, c) for k, c in enumerate(text) if norm(c)]
    st = [None] * len(text); en = [None] * len(text)
    sm = difflib.SequenceMatcher(None, "".join(c for _, c in S), "".join(C), autojunk=False)
    for x, y, n in sm.get_matching_blocks():
        for j in range(n): k = S[x + j][0]; st[k], en[k] = CT[y + j]
    known = [k for k in range(len(text)) if st[k] is not None]
    if not known: return [0.0] * len(text), [0.0] * len(text), 0.0
    for k in range(len(text)):
        if st[k] is None:
            p = max([q for q in known if q < k], default=None); n_ = min([q for q in known if q > k], default=None)
            if p is None: st[k] = en[k] = max(0, st[n_] - 0.05 * (n_ - k))
            elif n_ is None: st[k] = en[k] = en[p] + 0.05 * (k - p)
            else: f = (k - p) / (n_ - p); st[k] = en[k] = en[p] + (st[n_] - en[p]) * f
    return [round(max(0, x), 3) for x in st], [round(max(0, x), 3) for x in en], len([k for k, _ in S if st[k] is not None]) / max(1, len(S))

def check_piece(p, text):
    """조각 하나 — 귀에 걸리는 증상(narr_frag 와 같은 잣대)"""
    db = env_db(load16(p)); R = runs(db); why = []
    snd = [r for r in R if not r[0]]; sil = [r for r in R if r[0] and r[2] - r[1] >= 0.2]
    if snd and sil and snd[0][2] - snd[0][1] < 0.35 and sil[0][1] <= snd[0][2] + 0.01: why.append(f"앞 토막 {snd[0][2] - snd[0][1]:.2f}초+쉼")
    if snd and sil and snd[-1][2] - snd[-1][1] < 0.35 and abs(sil[-1][2] - snd[-1][1]) < 0.011: why.append(f"끝 토막 {snd[-1][2] - snd[-1][1]:.2f}초")
    d = len(db) * HOP; n = len(norm(text)); cps = n / max(d, 0.1)
    if n >= 6 and not 3.0 <= cps <= 11.0: why.append(f"길이 이상 {d:.1f}초/{n}자({cps:.1f}자/초)")
    return why

def frag_ok(p, text, why):
    """앞·끝 토막이 잡히면 조각을 받아써(Groq) 그 토막이 대본 첫·끝 낱말인지(「이제,」「하지만」「그런데」) 본다.
    이웃 문장 토막이면 받아쓴 첫 낱말이 대본 첫 낱말과 다르고 둘째 낱말이 대본 첫 낱말이 된다(16 핀치 「고 로봇은…」)."""
    m = p[:-4] + "_chk.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ac", "1", "-ar", "16000", "-b:a", "64k", m], check=True)
    ws = [norm(w["word"]) for w in (asr_groq(m) if os.path.exists(os.path.expanduser("~/.volcano/keys/groq")) else asr_sm(m))]; os.remove(m)  # Groq 열쇠 없는 PC(10-19) → Speechmatics; ws = [w for w in ws if w]
    t = [norm(x) for x in text.split()]; t = [x for x in t if x]
    if not ws or not t: return why
    keep = []
    for y in why:
        if y.startswith("앞 토막"):
            if ws[0][:1] == t[0][:1] and not (len(ws) > 1 and ws[1][:2] == t[0][:2] and ws[0][:2] != t[0][:2]): continue
            keep.append(y + f" (들림 「{' '.join(ws[:2])}」 / 대본 「{t[0]}」)")
        elif y.startswith("끝 토막"):
            if ws[-1][-1:] == t[-1][-1:]: continue
            keep.append(y + f" (들림 「{' '.join(ws[-2:])}」 / 대본 「{t[-1]}」)")
        else: keep.append(y)
    return keep

if __name__ == "__main__":
    wav, n0, n1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    OUT = arg("--out", "narr"); HOW = arg("--asr", "sm"); ITEMS = arg("--items", "items.json")
    # 나레 빠르기(atempo, 음높이 그대로 · 글자 시각도 같은 배율). ★10-19 "1.35배" 는 쇼츠 나레 얘기 — "아니. 쇼츠 말하는거야" · "롱은 그대로" → 롱폼 기본 1배
    SPEED = float(arg("--speed", (json.load(open("ep.json", encoding="utf-8")) if os.path.exists("ep.json") else {}).get("narr_speed", 1.0)))
    items = {q["ni"]: q["text"] for q in json.load(open(ITEMS, encoding="utf-8")) if q["type"] == "N"}
    texts = [(i, items[i]) for i in batch_ids(n0, n1)]
    db = env_db(load16(wav)); W = words_of(wav, HOW)
    segs, Wn, log = split(wav, texts, W, db); os.makedirs(OUT, exist_ok=True)
    for ni, c0, c1, rule in log:
        if rule != "R3": print(f"  경계 n{ni:03d}| {c0:.2f} → {c1:.2f} {rule}")
    bad = []; gp = gaps(db)
    for q in range(len(segs) - 1):            # 마지막 경계를 규칙으로 다시 재 봄 — 옮길 데가 남았으면(앞으로만 밀기 등) 실패. 16 핀치 옛 경계 97곳 중 문제 55곳을 이걸로 잡음
        e = segs[q][1]; c, r = refine(e, db, gp, texts[q + 1][1])
        if abs(c - e) > 0.03 and r != "R3": bad.append((texts[q][0], [f"끝 경계 {e:.2f} 가 소리 토막 옆 ({r} → {c:.2f})"]))
    for (ni, t), (a, b) in zip(texts, segs):
        a2, b2 = trim(db, a, b)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a2:.3f}", "-to", f"{b2:.3f}", "-i", wav, "-af", f"afade=t=in:d=0.012,afade=t=out:st={max(0, b2 - a2 - 0.025):.3f}:d=0.025,"
                        + (f"atempo={SPEED:.4f}," if SPEED != 1 else "") + "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000", "-ac", "2", f"{OUT}/n{ni:03d}.wav"], check=True)
        st, en, cov = char_times(t, a2, Wn)
        if SPEED != 1: st = [round(x / SPEED, 3) for x in st]; en = [round(x / SPEED, 3) for x in en]
        json.dump({"text": t, "chars": list(t), "st": st, "en": en, "src": [wav, round(a, 3), round(b, 3)], "trim": [round(a2, 3), round(b2, 3)], "asr": HOW, "cover": round(cov, 2)},
                  open(f"{OUT}/n{ni:03d}.json", "w", encoding="utf-8"), ensure_ascii=False)
        why = check_piece(f"{OUT}/n{ni:03d}.wav", t)
        if any(y.startswith(("앞 토막", "끝 토막")) for y in why): why = frag_ok(f"{OUT}/n{ni:03d}.wav", t, why)
        if cov < 0.5: why.append(f"받아쓰기 짝 {cov:.0%}")
        for e in (a, b):                      # 경계가 소리 속(앞뒤 10ms 가장 조용한 칸도 −40dB 넘음) — 문장을 이어 읽어 쉼이 없는 곳은 R4 가 가장 조용한 곳을 고른다
            k = int(round(e / HOP))
            if 0 < k < len(db) - 1 and db[k - 1:k + 2].min() > -30: why.append(f"경계 소리 속 {e:.2f}초 {db[k - 1:k + 2].min():.0f}dB")
        if why: bad.append((ni, why))
        print(ni, f"{a2:.2f}-{b2:.2f}", round(b2 - a2, 2), t[:20], ("  ← " + " · ".join(why)) if why else "", flush=True)
    print(f"조각 {len(texts)} · 증상 {len(bad)}")
    if bad:
        for ni, why in bad: print(f"  n{ni:03d}", " · ".join(why))
        sys.exit(1)
