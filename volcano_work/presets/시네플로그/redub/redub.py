# -*- coding: utf-8 -*-
"""남의 리뷰 영상(허락 받음) 나레이션만 바꿔 끼우기. 10-31 텔레그램 사용자 「8번영상찾아서 나래이션만 바꿔줘」·「허락받았어」
(영화씨 「이별, 그 뒤에도」 eRzW8h5qZqI). 화면·드라마 대사 소리는 그대로.
폴더 W 안에 src.mp4 · subs.ko.vtt(채널이 올린 나레 자막 = 나레 구간) · sep/htdemucs/a/no_vocals.wav(demucs) 가 있어야 한다.
  python redub.py rewrite W   나레 덩어리(자막 간격 0.6초 미만 이음)마다 같은 뜻 다른 문장(글자 수 원문 이하) → narr_new.json
  python redub.py tts W       ElevenLabs 녹음 → narr/bNNN.wav (덩어리 길이 넘으면 1.15배까지 빠르게, 넘으면 다시 줄여 쓰기)
  python redub.py mix W       나레 구간만 원음 → no_vocals(나레 뺀 배경)로 바꾸고 새 나레 얹음 → final.mp4 (-16 LUFS)"""
import json, os, re, subprocess, sys, base64, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "b판"))
VOICE = "K349x43DIDecCYoQWw7U"     # ElevenLabs Ethan - Deep
PAD = 0.15


def blocks(W):
    nb = os.path.join(W, "narr_blocks.json")      # 자막 없는 영상: 받아쓰기+목소리(resemblyzer)+제브로 고른 나레 덩어리
    if os.path.exists(nb): return [[b["a"], b["b"], b["t"]] for b in json.load(open(nb, encoding="utf-8"))]
    t = open(os.path.join(W, "subs.ko.vtt"), encoding="utf-8").read(); C = []
    for m in re.finditer(r"(\d+):(\d+):([\d.]+) --> (\d+):(\d+):([\d.]+)[^\n]*\n(.+?)(?:\n\n|\Z)", t, re.S):
        a = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]); b = int(m[4]) * 3600 + int(m[5]) * 60 + float(m[6])
        C.append([a, b, m[7].replace("\n", " ").strip()])
    B = []
    for c in C:
        if B and c[0] - B[-1][1] < 0.6: B[-1][1] = c[1]; B[-1][2] += " " + c[2]
        else: B.append(list(c))
    return B


def spans(W):
    """11-01 친애하는 X: whisper 가 대사를 못 받아쓰면 앞 낱말 하나를 10초씩 늘려 잡아 나레 덩어리 안에 대사가 통째로 들어감
    (덩어리 전체를 배경으로 바꾸면 그 대사 소리·자막이 사라짐). → 덩어리마다 실제로 소리 낸 구간만:
    너무 긴 낱말은 글자 수만큼으로 줄이고(다음 낱말에 붙어 있으면 앞을, 아니면 뒤를 깎음) 0.6초 미만 틈은 잇고, 새 나레 녹음 길이 구간도 더한다.
    → [[ [s, e], ... ] 덩어리 순서]  (PAD 는 안 붙임)"""
    B = blocks(W); nb = os.path.join(W, "narr_blocks.json"); fitp = os.path.join(W, "tts_fit.json")
    R = {r[0]: r[1] for r in json.load(open(fitp))} if os.path.exists(fitp) else {}
    raw = json.load(open(nb, encoding="utf-8")) if os.path.exists(nb) else None
    if not raw or "ids" not in raw[0]:
        return [[[a, max(b, a - 0.05 + R.get(i, b - a))]] for i, (a, b, _) in enumerate(B)]
    C = json.load(open(os.path.join(W, "chunks.json"), encoding="utf-8"))
    Wd = json.load(open(os.path.join(W, "asr.json"), encoding="utf-8"))["words"]
    fix = []
    for k, w in enumerate(Wd):
        s, e = w["start"], w["end"]; est = 0.15 * len(w["word"].strip()) + 0.4
        if e - s > max(1.2, est):
            if k + 1 < len(Wd) and Wd[k + 1]["start"] - e < 0.15: s = e - est
            else: e = s + est
        fix.append((w["start"], s, e))
    import bisect
    st = [f[0] for f in fix]; out = []
    for i, bl in enumerate(raw):
        iv = []
        for cid in bl["ids"]:
            c = C[cid]
            for _, s, e in fix[bisect.bisect_left(st, c["a"] - 0.01):bisect.bisect_right(st, c["b"])]:
                if iv and s - iv[-1][1] < 0.6: iv[-1][1] = max(iv[-1][1], e)
                else: iv.append([s, e])
        a = B[i][0]; iv.append([max(0, a - 0.05), a - 0.05 + R.get(i, B[i][1] - a)])
        iv.sort(); M = []
        for s, e in iv:
            if M and s - M[-1][1] < 0.6: M[-1][1] = max(M[-1][1], e)
            else: M.append([s, e])
        out.append(M)
    return out


def resplit(W):
    """11-01 spans 와 같은 낱말 고침으로 덩어리 안에 0.6초 넘는 틈(=놓친 대사)이 있으면 그 덩어리를 틈마다 쪼갠다.
    안 쪼갠 덩어리는 새 문장(narr_new.json)·녹음(narr/nNNN.wav·json)을 새 번호로 옮기고, 쪼갠 조각만 rewrite·녹음을 다시 한다. 옛것은 W/_pre_resplit/."""
    import shutil, bisect
    nb = os.path.join(W, "narr_blocks.json"); bk = os.path.join(W, "_pre_resplit")
    raw = json.load(open(os.path.join(bk if os.path.exists(os.path.join(bk, "narr_blocks.json")) else W, "narr_blocks.json"), encoding="utf-8"))
    C = json.load(open(os.path.join(W, "chunks.json"), encoding="utf-8"))
    Wd = json.load(open(os.path.join(W, "asr.json"), encoding="utf-8"))["words"]
    fix = []
    for k, w in enumerate(Wd):
        s, e = w["start"], w["end"]; est = 0.15 * len(w["word"].strip()) + 0.4
        if e - s > max(1.2, est):
            if k + 1 < len(Wd) and Wd[k + 1]["start"] - e < 0.15: s = e - est
            else: e = s + est
        fix.append((w["start"], s, e, w["word"].strip()))
    st = [f[0] for f in fix]; NB = []; mp = {}
    for i, bl in enumerate(raw):
        runs = []
        for cid in bl["ids"]:
            c = C[cid]
            for _, s, e, t in fix[bisect.bisect_left(st, c["a"] - 0.01):bisect.bisect_right(st, c["b"])]:
                if runs and s - runs[-1]["b"] < 0.6: runs[-1]["b"] = max(runs[-1]["b"], e); runs[-1]["t"] += " " + t
                else: runs.append({"a": s, "b": e, "t": t, "ids": [cid]})
        # 「그」「바로 그때」 같은 짧은 조각(공백 빼고 5자 이하)은 홀로 녹음하면 「이」「때 준서가…」처럼 깨짐 → 뒤 조각 바로 앞에 붙임(마지막이면 앞 조각에)
        k = 0
        while len(runs) > 1 and k < len(runs):
            r = runs[k]
            if len(r["t"].replace(" ", "")) <= 5:
                if k + 1 < len(runs):
                    n = runs[k + 1]; n["a"] = n["a"] - min(0.8, r["b"] - r["a"]); n["t"] = r["t"] + " " + n["t"]; n["ids"] = r["ids"] + n["ids"]
                else:
                    q = runs[k - 1]; q["b"] = q["b"] + min(0.8, r["b"] - r["a"]); q["t"] += " " + r["t"]
                runs.pop(k); continue
            k += 1
        if len(runs) <= 1: mp[i] = len(NB); NB.append(bl)
        else: NB.extend(runs)
    first = not os.path.exists(os.path.join(bk, "narr_blocks.json")); os.makedirs(bk, exist_ok=True)
    if first:
        for x in ("narr_blocks.json", "narr_new.json", "tts_fit.json"):
            if os.path.exists(os.path.join(W, x)): shutil.copy(os.path.join(W, x), bk)
    pn = os.path.join(bk, "narr_new.json")           # 11-01 새 편은 split 바로 뒤(rewrite·녹음 전)에 돌려도 됨
    N = json.load(open(pn, encoding="utf-8")) if os.path.exists(pn) else {}
    nd = os.path.join(W, "narr"); od = os.path.join(bk, "narr")
    if first and os.path.exists(nd): shutil.move(nd, od)
    else: shutil.rmtree(nd, ignore_errors=True)             # 다시 돌릴 땐 새 번호로 처음부터 옮김
    os.makedirs(nd, exist_ok=True)
    for i, j in mp.items():
        for ext in ("wav", "json"):
            f = os.path.join(od, f"n{i+1:03d}.{ext}")
            if os.path.exists(f): shutil.copy(f, os.path.join(nd, f"n{j+1:03d}.{ext}"))
    json.dump({str(j): N[str(i)] for i, j in mp.items() if str(i) in N}, open(os.path.join(W, "narr_new.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(NB, open(nb, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("덩어리", len(raw), "→", len(NB), "· 쪼갠 덩어리", len(raw) - len(mp), "· 새로 쓸 조각", len(NB) - len(mp))


def rewrite(W):
    import make_b as MB
    B = blocks(W); out = os.path.join(W, "narr_new.json")
    N = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else {}
    title = open(os.path.join(W, "title.txt"), encoding="utf-8").read().strip()
    def job(part):
        ctx = "\n".join(f"{j}. {B[j][2]}" for j in range(max(0, part[0] - 5), min(len(B), part[-1] + 6)))
        req = "\n".join(f'{i}. (최대 {len(B[i][2])}자) {B[i][2]}' for i in part)
        p = (f"아래는 드라마 「{title}」 리뷰·몰아보기 영상의 나레이션 일부다(받아쓰기라 오타가 있을 수 있다 — 인물 이름·고유명사는 드라마 기준으로 바로잡아라).\n" + ctx +
             "\n\n이 중 아래 번호 줄들을 뜻·사실·인물 이름은 그대로 두고 문장 구조와 낱말을 바꿔 새로 써라. "
             "원문과 같은 어절이 세 개 넘게 이어지면 안 된다(아주 짧은 이음말 줄은 비슷한 다른 이음말로). 말투는 유튜브 리뷰 나레이션(~하는데요, ~합니다 섞어서). "
             "괄호 안 글자 수를 넘기지 마라. 큰따옴표 대신 작은따옴표.\n출력은 JSON 객체 하나만: {\"번호\": \"새 문장\", ...}\n\n" + req)
        r = MB.ask(p); m = re.search(r"\{.*\}", r, re.S)
        try: return part, json.loads(m.group(0)) if m else {}
        except Exception: return part, {}
    for tries in range(6):
        todo = [i for i in range(len(B)) if str(i) not in N]
        if not todo: break
        with ThreadPoolExecutor(4) as ex:      # 10-31 빈센조 830덩어리 — agy 4개 동시
            for part, d in ex.map(job, [todo[k:k + 25] for k in range(0, len(todo), 25)]):
                for i in part:
                    s = (d.get(str(i)) or "").strip()
                    if s and len(s) <= len(B[i][2]) + 2 and s != B[i][2]: N[str(i)] = s
                json.dump(N, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                print("rewrite", len(N), "/", len(B), flush=True)
    print("못 바꾼 줄", [i for i in range(len(B)) if str(i) not in N])


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


def tts(W):
    K = open(os.path.expanduser("~/.volcano/keys/elevenlabs")).read().strip()
    B = blocks(W); N = json.load(open(os.path.join(W, "narr_new.json"), encoding="utf-8"))
    os.makedirs(os.path.join(W, "narr"), exist_ok=True)
    def one(i):
        text = N[str(i)]; mp3, js, wav = (os.path.join(W, f"narr/b{i:03d}.{e}") for e in ("mp3", "json", "wav"))
        if not (os.path.exists(js) and json.load(open(js, encoding="utf-8")).get("text") == text):
            body = json.dumps({"text": text, "model_id": "eleven_v3",
                               "voice_settings": {"stability": 0.5, "similarity_boost": 0.71}}, ensure_ascii=False).encode()
            for t in range(60):                 # 11-01 동시 요청 5개 한도(429 concurrent) — 여러 편 같이 돌리면 오래 기다림
                try:
                    r = urllib.request.urlopen(urllib.request.Request(
                        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
                        data=body, headers={"xi-api-key": K, "Content-Type": "application/json"}), timeout=300)
                    open(mp3, "wb").write(r.read()); break
                except urllib.error.HTTPError as e:
                    print(i, e.code, e.read()[:200], flush=True)
                    if e.code in (429, 500, 502, 503): time.sleep(20); continue
                    raise
            else: raise RuntimeError(f"tts {i} 429 계속")
            json.dump({"text": text}, open(js, "w", encoding="utf-8"), ensure_ascii=False)
        room = B[i][1] - B[i][0] + 2 * PAD; d = dur(mp3)
        sp = min(max(1.0, d / room), 1.15)
        af = f"silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,atempo={sp:.3f},aresample=48000"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-af", af, "-ac", "2", wav], check=True)
        return i, round(dur(wav), 2), round(room, 2)
    with ThreadPoolExecutor(2) as ex: R = list(ex.map(one, range(len(B))))   # 11-01 3→2: 편 두 개 같이 돌아도 동시 4개
    over = [r for r in R if r[1] > r[2] + 0.3]
    json.dump(R, open(os.path.join(W, "tts_fit.json"), "w"))
    print("tts", len(R), "넘침", over)


def gemprep(W):
    """제미나이 3.8(AI 스튜디오) 녹음 준비: script.py(N 줄 = 덩어리 순서) → mkbatch → READY. recv.py·splitwatch 가 narr/nNNN.wav 로 자름."""
    B = blocks(W); N = json.load(open(os.path.join(W, "narr_new.json"), encoding="utf-8"))
    miss = [i for i in range(len(B)) if str(i) not in N]
    if miss: sys.exit(f"못 바꾼 줄 {miss[:20]}")
    open(os.path.join(W, "script.py"), "w", encoding="utf-8").write(
        "S = [\n" + "".join(f'("N", {json.dumps(N[str(i)], ensure_ascii=False)}),\n' for i in range(len(B))) + "]\n")
    subprocess.run([sys.executable, os.path.join(HERE, "..", "v9", "prep", "mkbatch.py"), "2000"], cwd=W, check=True)
    open(os.path.join(W, "READY"), "w").close()


def fit(W):
    """제미나이 녹음(narr/nNNN.wav, 1부터) → 덩어리 자리에 맞춤 narr/bNNN.wav (앞뒤 무음 깎고, 넘치면 1.15배까지 빠르게)."""
    B = blocks(W); R = []
    for i in range(len(B)):
        src = os.path.join(W, f"narr/n{i+1:03d}.wav"); out = os.path.join(W, f"narr/b{i:03d}.wav")
        room = B[i][1] - B[i][0] + 2 * PAD
        tmp = out + ".trim.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                        "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                        "-ar", "48000", "-ac", "2", tmp], check=True)
        d = dur(tmp); sp = min(max(1.0, d / room), 1.15)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"atempo={sp:.3f},loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000", "-ac", "2", out], check=True)
        os.remove(tmp); R.append((i, round(dur(out), 2), round(room, 2)))
    over = [r for r in R if r[1] > r[2] + 0.3]
    json.dump(R, open(os.path.join(W, "tts_fit.json"), "w"))
    print("fit", len(R), "넘침", len(over), over[:30])


def subs(W, y=615, size=58):   # 10-31 사용자 「글자가너무작은데」 40→58 · 「화면위에」 검은 띠→그림 아래쪽
    """새 나레 자막만(대사엔 글자 없음 — 10-31 사용자 「대사는 글자넣지마」) → narr.ass. 덩어리 시작부터 녹음 길이만큼, 24자 넘으면 글자 수 비례로 나눠 차례로."""
    B = blocks(W); N = json.load(open(os.path.join(W, "narr_new.json"), encoding="utf-8"))
    R = {r[0]: r[1] for r in json.load(open(os.path.join(W, "tts_fit.json")))}
    ts = lambda t: f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1280", "PlayResY: 720", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         f"Style: N,Malgun Gothic,{int(size)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,1,2,30,30,{720-int(y)},1", "",
         "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for i, (a, b, _) in enumerate(B):
        t = N[str(i)].strip(); d = R.get(i, b - a); a0 = max(0, a - 0.05)
        ws = t.split(); k = max(1, -(-len(t) // 20)); parts = []     # 20자 넘으면 k 줄로 고르게(꼬리 「뜻하죠.」만 따로 남지 않게)
        for j in range(k):
            tgt = len(t) * (j + 1) / k; cur = []
            while ws and (j == k - 1 or not cur or len(" ".join(sum(parts and [p.split() for p in parts] or [], []) + cur + [ws[0]])) <= tgt + 3):
                cur.append(ws.pop(0))
            if cur: parts.append(" ".join(cur))
        tot = sum(len(x) for x in parts) or 1; c = a0
        for x in parts:
            e = c + d * len(x) / tot; L.append(f"Dialogue: 0,{ts(c)},{ts(e)},N,,0,0,0,,{x}"); c = e
    # 10-31 사용자 「처음에 외국어하는 대사는 좀적어줘」 → dlg_subs.json [[a, b, "줄1\\N줄2"], ...] 있으면 외국어 대사 자막(옛 박힌 자막을 읽어 옮긴 것)도. 나레 덩어리와 겹치지 않게 자른다.
    p = os.path.join(W, "dlg_subs.json")
    if os.path.exists(p):
        L.insert([k for k, s in enumerate(L) if s.startswith("Style: N")][0] + 1, f"Style: D,Malgun Gothic,{int(size) - 8},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,1,2,30,30,{720-int(y)},1")
        for a, b, t in json.load(open(p, encoding="utf-8")):
            for x, z, _ in B:
                if x - 0.05 < b and z > a:
                    if x > a: b = min(b, x - 0.05)
                    else: a = max(a, z)
            if b - a > 0.3: L.append(f"Dialogue: 0,{ts(a)},{ts(b)},D,,0,0,0,,{t}")
    open(os.path.join(W, "narr.ass"), "w", encoding="utf-8-sig").write("\n".join(L) + "\n")
    print("subs", len(B))


def mix(W, video=None, delogo=None):
    """나레 구간(+PAD)만 원음 → no_vocals(나레 뺀 배경)로 바꾸고 새 나레(narr/bNNN.wav)를 얹는다. 60초씩 numpy 로(830덩어리 ffmpeg 필터는 너무 무거움).
    video: 화면 원본(없으면 src.mp4) · delogo: "x:y:w:h" 채널 글자 지우기(지우면 h264_nvenc 로 다시 굽고, 아니면 화면 복사)."""
    import numpy as np, soundfile as sf
    B = blocks(W); SR = 48000; F = int(0.08 * SR)
    video = video or os.path.join(W, "src.mp4")
    orig, bg, mixw = (os.path.join(W, x) for x in ("_orig48.w64", "_bg48.w64", "_mix48.w64"))   # 11-01 션샤인 6시간: wav 는 4GB 넘으면 깨짐 → w64
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(W, "src.mp4"), "-vn", "-ac", "2", "-ar", str(SR), orig], check=True)
    dl = os.path.join(W, "dm", "list.txt")                # 10분 토막이 있으면 그걸 바로 잇는다(합친 no_vocals.wav 가 4GB 넘으면 깨짐)
    bin_ = ["-f", "concat", "-safe", "0", "-i", dl] if os.path.exists(dl) else ["-i", os.path.join(W, "sep", "htdemucs", "a", "no_vocals.wav")]
    subprocess.run(["ffmpeg", "-v", "error", "-y", *bin_, "-ac", "2", "-ar", str(SR), bg], check=True)
    fo, fb = sf.SoundFile(orig), sf.SoundFile(bg); n = fo.frames
    g = np.zeros(n, dtype=np.float32)                     # 1 = 나레 구간(배경만)
    ramp = np.linspace(0, 1, F, dtype=np.float32)
    for a, b in (x for sp in spans(W) for x in sp):       # 11-01 덩어리 전체 말고 실제 소리 낸 구간만(spans)
        i0, i1 = min(n, max(0, int((a - PAD) * SR))), min(n, int((b + PAD) * SR)); g[i0:i1] = 1   # 11-01 션샤인: 끝 넘는 구간
        j0 = max(0, i0 - F); g[j0:i0] = np.maximum(g[j0:i0], ramp[F - (i0 - j0):])
        j1 = min(n, i1 + F); g[i1:j1] = np.maximum(g[i1:j1], ramp[::-1][:j1 - i1])
    nar = []                                             # (시작 샘플, 소리)
    for i, (a, b, _) in enumerate(B):
        x, sr = sf.read(os.path.join(W, f"narr/b{i:03d}.wav"), dtype="float32", always_2d=True)
        nar.append((int(max(0, a - 0.05) * SR), x))
    out = sf.SoundFile(mixw, "w", SR, 2, "PCM_24"); CH = 60 * SR; k = 0
    while k < n:
        m = min(CH, n - k); o = fo.read(m, dtype="float32", always_2d=True); bb = fb.read(m, dtype="float32", always_2d=True)
        if len(bb) < m: bb = np.vstack([bb, np.zeros((m - len(bb), 2), np.float32)])
        gg = g[k:k + m, None]; y = o * (1 - gg) + bb * gg
        for s0, x in nar:
            if s0 < k + m and s0 + len(x) > k:
                a0, a1 = max(s0, k), min(s0 + len(x), k + m); y[a0 - k:a1 - k] += x[a0 - s0:a1 - s0]
        out.write(y); k += m
    out.close()
    # delogo 자리에 ffmpeg 화면 필터 전체를 줄 수도 있다(「=」 들어가면 그대로 · 「@파일」이면 파일 내용 — zoomvf 가 만든 vf.txt). 화면을 고치면 h264_nvenc 로 다시 굽는다.
    if delogo and delogo.startswith("@"): delogo = open(delogo[1:], encoding="utf-8").read().strip()
    if delogo and "=" not in delogo: delogo = "delogo=x={}:y={}:w={}:h={}".format(*delogo.split(":"))
    vf = ["-vf", delogo, "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "23"] if delogo else ["-c:v", "copy"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", mixw, "-map", "0:v", "-map", "1:a", *vf,
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", "-c:a", "aac", "-b:a", "192k",
                    os.path.join(W, "final.mp4")], check=True)
    r = subprocess.run(["ffmpeg", "-i", os.path.join(W, "final.mp4"), "-vn", "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    print("final", round(dur(os.path.join(W, "final.mp4")), 1), "s", re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1:], "LUFS")


def zoomvf(W, crop="1067:600:200:0", delogo="1045:632:210:66"):
    """10-31 우아한 가 사용자 「옛자막 그대로 쓰자」+「나래이션부분에는 확대해서 글자없애고 우리나래로」:
    나레 동안만 crop(확대)한 화면으로 바꾸고(박힌 나레 자막·채널 글자가 화면 밖으로), 대사 동안은 원래 화면+채널 글자만 지움. 새 나레 자막(narr.ass)을 얹는다.
    → W/zoom_cmds.txt(sendcmd) · W/vf.txt  (mix W 화면 @W/vf.txt 로 쓴다)"""
    iv = []
    for s, e in sorted(x for sp in spans(W) for x in sp):     # 11-01 실제 소리 낸 구간만 확대(대사 자막 안 잘리게)
        s, e = max(0, s - PAD), e + PAD
        if iv and s - iv[-1][1] < 1.0: iv[-1][1] = max(iv[-1][1], e)      # 1초 안 틈은 이어서(깜빡임 막기)
        else: iv.append([s, e])
    cp = os.path.join(W, "zoom_cmds.txt")
    open(cp, "w", encoding="utf-8").write("".join(f"{s:.2f}-{e:.2f} [enter] streamselect@z map 1, [leave] streamselect@z map 0;\n" for s, e in iv))
    esc = lambda p: p.replace("\\", "/").replace(":", "\\:")
    dl = "" if delogo == "none" else "delogo=x={}:y={}:w={}:h={},".format(*delogo.split(":"))   # 11-01 메스: 채널 글자 없는 영상은 none
    vf = (f"sendcmd=f='{esc(cp)}',split[o][z];[z]crop={crop},scale=1280:720,setsar=1[zz];[o]{dl}setsar=1[od];"
          f"[od][zz]streamselect@z=inputs=2:map=0,subtitles='{esc(os.path.join(W, 'narr.ass'))}'")
    open(os.path.join(W, "vf.txt"), "w", encoding="utf-8").write(vf)
    print("zoom 구간", len(iv), "초", round(sum(e - s for s, e in iv)), "→ vf.txt")


if __name__ == "__main__":
    {"rewrite": rewrite, "tts": tts, "gemprep": gemprep, "fit": fit, "subs": subs, "mix": mix, "zoomvf": zoomvf, "resplit": resplit}[sys.argv[1]](*sys.argv[2:])
