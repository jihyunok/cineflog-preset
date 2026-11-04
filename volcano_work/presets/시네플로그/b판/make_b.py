# -*- coding: utf-8 -*-
"""시네플로그 완성 편 → 무비세상(B채널) 판. 10-31 텔레그램 사용자:
 "시네플로그 영화만든거 같은영화를 길이를좀줄여서 나래이션 새로넣어서 b채널에 올릴수있게 만들어줘"
 "2분정도만줄이고 무비세상으로해줘" · "4번은그대로다변경"(대본 새로·목소리 바꿈) · "할수있는영화는다 b버전만들어줘 싹다"
A판(D:/cine_work/epNN_제목) 대본·조각 구간은 그대로 두고:
 ① 나레 문장 전부 새로(뜻·사실·이름 같게, 말투·문장 다르게, 글자 수 A판 이하) — agy
 ② 목소리 ElevenLabs Ethan(A판 민준 대신)
 ③ 앞 6분·끝 4분 밖의 대사 창(자동 dauto 먼저)을 빼서 약 2분 줄임
 ④ 화면 위 글자 「무비세상」
조각(clips)은 A판 폴더 것을 같이 씀(이름이 내용 그대로라 같은 조각은 다시 안 자름).
사용(B판 폴더 D:/cine_work/epNNb_제목 를 만들고 그 안에서 단계별로):
  python make_b.py init  <A판 폴더>      폴더·ep.json·대본 사본, 뺄 대사 창 고름(b_drop.json)
  python make_b.py rewrite <B판 폴더>    나레 새로 쓰기(narr_b.json) → script.py 에 넣기
  python make_b.py emph <B판 폴더>       지무비식 강조 말을 새 문장에서 다시 고름
  python make_b.py tts <B판 폴더>        ElevenLabs Ethan 녹음 → narr/
이후 v9 순서 그대로: plan_v9 → narr_pic → gate pre → build_v9 cut → build_v9 (run_b.sh)."""
import ast, json, os, re, shutil, subprocess, sys
VOICE = "K349x43DIDecCYoQWw7U"          # ElevenLabs 「Ethan - Deep」 ko 남자(A판 민준 DkAJhrMznCtWh38YrjTv 와 다르게)
BRAND = "무비세상"
CUT_TARGET = 85.0                        # 약 2분(대사 창 85초 + 나레 짧아짐·자리 없는 소리 장면 빠짐 ≈ 2분, 33b 는 120 으로 2:49 줄어듦)
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
SKIP_DIRS = {"clips", "narr", "_fs", "_np", "썸네일보기", "_capcut_draft_old_1027", "narr_ludo"}
SKIP_EXT = (".mkv", ".mp4", ".wav", ".mp3", ".jpg", ".png", ".log")


def load_S(path):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S")
    ns = {}; cwd = os.getcwd(); os.chdir(os.path.dirname(os.path.abspath(path)))   # 옛 편 대본은 lines.json 을 읽음(10-31 ep20)
    try: exec(src, ns)
    finally: os.chdir(cwd)
    return src, node.value.elts, ns["S"]


def ask(p, model=None):
    model = model or os.environ.get("AGY_MODEL", "gemini-3.8-flash-high")
    try:
        r = subprocess.run([AGY, "--model", model, "-p", p + "\n도구를 쓰지 말고 답해줘.", "--print-timeout", "900s"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1200)
    except subprocess.TimeoutExpired:
        return ""                          # 10-31 ep29 emph 에서 agy 가 75분 넘게 멈춤 → 20분에 끊음
    return r.stdout


def init(A):
    A = A.rstrip("/\\"); base = os.path.basename(A); m = re.match(r"ep(\d+)(?:v\d+)?_(.+)", base)
    B = os.path.join(os.path.dirname(A), f"ep{m.group(1)}b_{m.group(2)}")
    os.makedirs(B, exist_ok=True)
    for f in os.listdir(A):
        p = os.path.join(A, f)
        if os.path.isdir(p):
            if f == "fonts" and not os.path.exists(os.path.join(B, f)): shutil.copytree(p, os.path.join(B, f))
            continue
        if f.endswith(SKIP_EXT) or f.startswith(("flipsheet", "npsheet", "finalcheck")): continue
        shutil.copy2(p, os.path.join(B, f))
    cfg = json.load(open(os.path.join(A, "ep.json"), encoding="utf-8"))
    if not os.path.isabs(cfg["src"]): cfg["src"] = os.path.join(A, cfg["src"]).replace("\\", "/")
    cfg["clips"] = os.path.join(A, cfg.get("clips", "clips")).replace("\\", "/")
    cfg["brand"] = BRAND
    cfg.pop("min_total", None)
    cfg["b_from"] = A.replace("\\", "/")
    json.dump(cfg, open(os.path.join(B, "ep.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    shutil.copy2(os.path.join(A, "script.py"), os.path.join(B, "script_A.py"))
    # ③ 뺄 대사 창 — A판 windows.json 의 실제 화면 길이로
    W = json.load(open(os.path.join(A, "windows.json"), encoding="utf-8"))
    total = W[-1]["b"]; dur, start = {}, {}
    for w in W:
        dur[w["k"]] = dur.get(w["k"], 0) + (w["b"] - w["a"]); start.setdefault(w["k"], w["a"])
    src, elts, S = load_S(os.path.join(A, "script.py")); lines = src.split("\n")
    emph = json.load(open(os.path.join(A, "emph.json"), encoding="utf-8")) if os.path.exists(os.path.join(A, "emph.json")) else {}
    yellow = emph.get("dlg_yellow", [])
    zone = None; cand = []
    for k, x in enumerate(S):
        if x[0] == "ZONE": zone = x[1]; continue
        if x[0] != "D" or zone != "main" or k not in dur: continue
        if start[k] < 360 or start[k] > total - 240: continue
        if isinstance(x[-1], dict) and x[-1].get("event"): continue
        if any(y in x[2] for y in yellow): continue
        auto = "dauto" in lines[elts[k].lineno - 1]
        cand.append((0 if auto else 1, k, dur[k]))
    # 고르게 퍼지게: 자동 대사 먼저, 그 안에서 화면 순서로 간격 두고
    def spread(pool, n):                  # 화면 순서로 고르게 n 개
        if n >= len(pool): return pool[:]
        return [pool[round(i * (len(pool) - 1) / max(1, n - 1))] for i in range(n)] if n > 1 else [pool[len(pool) // 2]]
    pick, got = [], 0.0
    for pri in (0, 1):
        pool = [c for c in cand if c[0] == pri and all(abs(c[1] - p) > 1 for p in pick)]
        if not pool or got >= CUT_TARGET: continue
        avg = sum(c[2] for c in pool) / len(pool)
        for c in sorted(spread(pool, int((CUT_TARGET - got) / avg) + 1), key=lambda c: c[1]):
            if got >= CUT_TARGET: break
            if any(abs(c[1] - p) <= 1 for p in pick): continue
            pick.append(c[1]); got += c[2]
    pick.sort()
    out = lines[:]
    for k in pick:
        e = elts[k]
        for ln in range(e.lineno - 1, e.end_lineno):
            out[ln] = "# B판 뺌 " + out[ln]
    open(os.path.join(B, "script.py"), "w", encoding="utf-8").write("\n".join(out))
    json.dump({"drop_k": pick, "sec": round(got, 1), "A_total": round(total, 1)}, open(os.path.join(B, "b_drop.json"), "w"), indent=0)
    print(B, "· 뺀 대사 창", len(pick), f"{got:.1f}초 · A판 {total / 60:.2f}분")


def more_cut(B, secs):
    """B판 계획(windows.json)이 A판보다 2분 덜 짧을 때(제미나이 목소리가 느림) 대사 창을 더 뺀다 — 10-31 26 투모로우 워 56초만 짧음."""
    secs = float(secs)
    W = json.load(open(os.path.join(B, "windows.json"), encoding="utf-8"))
    total = W[-1]["b"]; dur, start = {}, {}
    for w in W:
        dur[w["k"]] = dur.get(w["k"], 0) + (w["b"] - w["a"]); start.setdefault(w["k"], w["a"])
    src, elts, S = load_S(os.path.join(B, "script.py")); lines = src.split("\n")
    emph = json.load(open(os.path.join(B, "emph.json"), encoding="utf-8")) if os.path.exists(os.path.join(B, "emph.json")) else {}
    yellow = emph.get("dlg_yellow", [])
    zone = None; cand = []
    for k, x in enumerate(S):
        if x[0] == "ZONE": zone = x[1]; continue
        if x[0] != "D" or zone != "main" or k not in dur: continue
        if start[k] < 360 or start[k] > total - 240: continue
        if isinstance(x[-1], dict) and x[-1].get("event"): continue
        if any(y in x[2] for y in yellow): continue
        cand.append((k, dur[k]))
    n = max(1, int(secs / (sum(c[1] for c in cand) / len(cand))) + 1)
    pick = [cand[round(i * (len(cand) - 1) / max(1, n - 1))] for i in range(min(n, len(cand)))]
    got = 0.0; out = lines[:]; done = []
    for k, d in pick:
        if got >= secs or any(abs(k - p) <= 1 for p in done): continue
        for ln in range(elts[k].lineno - 1, elts[k].end_lineno): out[ln] = "# B판 더 뺌 " + out[ln]
        got += d; done.append(k)
    open(os.path.join(B, "script.py"), "w", encoding="utf-8").write("\n".join(out))
    print("더 뺀 대사 창", len(done), f"{got:.1f}초")


def rewrite(B):
    cfg = json.load(open(os.path.join(B, "ep.json"), encoding="utf-8"))
    src, elts, S = load_S(os.path.join(B, "script.py"))
    NT = [(k, x[1]) for k, x in enumerate(S) if x[0] == "N"]
    path = os.path.join(B, "narr_b.json")
    done = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    rule = ("너는 유튜브 영화 리뷰 채널의 나레이션 작가다. 아래는 다른 채널에 이미 올라간 같은 영화 리뷰의 나레이션 줄이다. "
            "같은 장면 위에 깔릴 새 나레이션을 줄마다 다시 써라.\n"
            "- 뜻·사실·인물 이름·순서는 그대로, 낱말과 문장 짜임은 확 다르게(같은 표현을 그대로 베끼지 말 것).\n"
            "- 글자 수는 원래 줄의 75~100% (더 길면 안 됨).\n"
            "- 말투: 「출발! 비디오 여행」처럼 장면을 설명하며 끌고 가는 해설체. ~합니다/~입니다 위주, ~죠 는 가끔, ~고요 금지, 「한편」 금지. 큰따옴표 금지.\n"
            "- 영화에 없는 사실을 지어내지 말 것.\n"
            f"영화 소개: {cfg.get('ctx', '')}\n인물 한국 이름: {cfg.get('who_ko', {})}\n"
            "입력 줄은 `번호\\t(최대 N자)\\t원래 문장` — 새 문장은 반드시 최대 N자 이하(띄어쓰기 포함).\n"
            "출력은 `번호\\t새 문장` 줄만, 모든 번호를 빠짐없이.\n\n")
    for tries in range(6):
        todo = [(i, t) for i, (k, t) in enumerate(NT, 1) if str(i) not in done]
        if not todo: break
        for c in range(0, len(todo), 40):
            part = todo[c:c + 40]
            out = ask(rule + "\n".join(f"{i}\t(최대 {len(t)}자)\t{t}" for i, t in part),
                      None)   # 10-31 클로드 할당량 막힘 → 늘 기본(AGY_MODEL 또는 제미나이)
            orig = dict(part)
            for m in re.finditer(r"^\s*(\d+)\t(.+?)\s*$", out, re.M):
                i = int(m.group(1)); t = re.sub(r"^\(최대 \d+자\)\t", "", m.group(2)).replace('"', "'").replace("\\", "").strip()
                if i not in orig: continue
                o = orig[i]
                if t == o or len(t) > len(o) * (1.05 if tries < 3 else 1.12) + 2 or len(t) < len(o) * 0.55: continue
                done[str(i)] = t
            json.dump(done, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print("rewrite", len(done), "/", len(NT), flush=True)
    miss = [i for i in range(1, len(NT) + 1) if str(i) not in done]
    if miss: print("못 바꾼 줄(A판 문장 그대로 둠):", miss)
    lines = src.split("\n")
    for i, (k, t) in enumerate(NT, 1):
        if str(i) not in done: continue
        node = elts[k].elts[1]; seg = ast.get_source_segment(src, node)
        ln = node.lineno - 1
        assert node.lineno == node.end_lineno and seg in lines[ln], (k, seg)
        lines[ln] = lines[ln].replace(seg, json.dumps(done[str(i)], ensure_ascii=False), 1)
    open(os.path.join(B, "script.py"), "w", encoding="utf-8").write("\n".join(lines))
    a = sum(len(t) for _, t in NT); b = sum(len(done.get(str(i), t)) for i, (_, t) in enumerate(NT, 1))
    print(f"나레 글자 A {a} → B {b}")


def emph(B):
    _, _, S = load_S(os.path.join(B, "script.py"))
    NT = [x[1] for x in S if x[0] == "N"]
    p = os.path.join(B, "emph.json"); E0 = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    body = "\n".join(f"{i}\t{t}" for i, t in enumerate(NT, 1))
    out = ask("아래 영화 리뷰 나레 줄마다, 화면 자막에서 크게 강조할 핵심 말(그 줄 글 안에 **글자 그대로** 있는 2~12자 토막)과 감정 하나를 골라라. "
              "감정은 emotion(뭉클·슬픔) · reveal(사실이 드러남) · twist(반전·뜻밖) · grad_slant(보통 강조) · threat(불안·위기) 중 하나. 강조할 게 없는 줄은 빼라. "
              "출력은 `번호\\t핵심 말\\t감정` 만.\n\n" + body)
    E = {}
    for m in re.finditer(r"^\s*(\d+)\t([^\t]+)\t(\w+)\s*$", out, re.M):
        n, ph, t = int(m.group(1)), m.group(2).strip(), m.group(3)
        if 1 <= n <= len(NT) and ph in NT[n - 1] and t in ("emotion", "reveal", "twist", "grad_slant", "threat", "kill", "climax", "money"): E[str(n)] = [ph, t]
    E0["n"] = E; E0["why_b"] = "10-31 무비세상 B판 — 새 나레 문장에서 강조 말 다시 고름(agy)"
    json.dump(E0, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("emph", len(E), "/", len(NT))


def tts(B):
    import base64, time, urllib.request, urllib.error
    from concurrent.futures import ThreadPoolExecutor
    K = open(os.path.expanduser("~/.volcano/keys/elevenlabs")).read().strip()
    _, _, S = load_S(os.path.join(B, "script.py"))
    NT = [x[1] for x in S if x[0] == "N"]
    os.makedirs(os.path.join(B, "narr"), exist_ok=True)
    def one(a):
        i, text = a
        raw, js, fin = (os.path.join(B, f"narr/n{i:03d}.{e}") for e in ("mp3", "json", "wav"))
        if os.path.exists(js) and os.path.exists(fin) and json.load(open(js, encoding="utf-8")).get("text") == text: return
        body = json.dumps({"text": text, "model_id": "eleven_v3",
                           "voice_settings": {"stability": 0.5, "similarity_boost": 0.71}}, ensure_ascii=False).encode("utf-8")
        for tries in range(6):
            try:
                r = urllib.request.urlopen(urllib.request.Request(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",
                    data=body, headers={"xi-api-key": K, "Content-Type": "application/json"}), timeout=300)
                d = json.load(r); break
            except urllib.error.HTTPError as e:
                msg = e.read().decode("utf-8", "replace")[:300]; print(i, e.code, msg, flush=True)
                if e.code in (429, 500, 502, 503): time.sleep(20); continue
                raise
        open(raw, "wb").write(base64.b64decode(d["audio_base64"]))
        al = d.get("alignment") or d.get("normalized_alignment")
        json.dump({"text": text, "voice": VOICE, "chars": al["characters"], "st": al["character_start_times_seconds"],
                   "en": al["character_end_times_seconds"]}, open(js, "w", encoding="utf-8"), ensure_ascii=False)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000", "-ac", "2", fin], check=True)
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(one, list(enumerate(NT, 1))))
    print("tts done", len(NT))


if __name__ == "__main__":
    {"init": init, "rewrite": rewrite, "emph": emph, "tts": tts, "more_cut": more_cut}[sys.argv[1]](*sys.argv[2:])
