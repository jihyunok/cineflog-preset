# -*- coding: utf-8 -*-
"""AI 스튜디오(Gemini 3.8 Flash TTS)에서 나레 여러 조각을 한 번에 뽑은 wav 를 조각별로 자른다.
Groq 단어 받아쓰기 → 아는 대본 글자 수로 조각 경계 단어를 찾고 → 그 근처 쉼(silencedetect) 가운데서 자른다.
결과: narr/nNNN.wav(-16 LUFS, 48k 스테레오) + narr/nNNN.json(chars/st/en — build_dr.py 자막 타이밍용, ElevenLabs 꼴)
사용: python gem_split.py 배치.wav 시작ni 끝ni
★10-13: 받아쓰기 낱말 시각이 0.1~0.3초 일러 경계가 소리 속에 떨어지기도 한다(「있었고」의 「고」가 다음 조각에) → 자른 뒤 ../ep16v5_핀치/narr_recut.py --dry · narr_frag.py 로 꼭 검사."""
import json, os, re, subprocess, sys, uuid, time, urllib.request, urllib.error
KEY = open(os.path.expanduser("~/.volcano/keys/groq"), encoding="utf-8").read().strip()
def asr(p):
    b = "----x" + uuid.uuid4().hex; parts = []
    for k, v in [("model","whisper-large-v3"),("response_format","verbose_json"),("temperature","0"),("language","ko"),("timestamp_granularities[]","word")]:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode()); parts.append(open(p,"rb").read()); parts.append(f"\r\n--{b}--\r\n".encode())
    while True:
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=b"".join(parts), headers={"Authorization":"Bearer "+KEY,"Content-Type":"multipart/form-data; boundary="+b,"User-Agent":"curl/8"}), timeout=300))
        except urllib.error.HTTPError as e:
            print("  ", e.code, e.read().decode()[:200], flush=True)
            if e.code == 429: time.sleep(40); continue
            if e.code >= 500: time.sleep(10); continue
            raise
def norm(s): return re.sub(r"[^0-9A-Za-z가-힣]", "", s)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout)

def split(wav, texts):
    """texts = [(ni, text)] 순서대로. 반환: 조각별 (a, b) 초."""
    sil = subprocess.run(["ffmpeg","-i",wav,"-af","silencedetect=n=-40dB:d=0.18","-f","null","-"],capture_output=True,text=True).stderr
    ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", sil)]; se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", sil)]
    gaps = list(zip(ss, se))
    D = dur(wav)
    # 받아쓰기는 약 50초 토막(쉼 가운데서 자름)으로 — 긴 파일 한 번에 넣으면 뒤쪽에 헛소리·시각 꼬임이 생긴다(b007)
    cj = wav[:-4] + "_asr2.json"
    if not os.path.exists(cj):
        cuts = [0.0]
        while D - cuts[-1] > 70:
            want = cuts[-1] + 50; g = min(gaps, key=lambda g: abs((g[0] + g[1]) / 2 - want) if (g[0] + g[1]) / 2 > cuts[-1] + 20 else 1e9)
            cuts.append((g[0] + g[1]) / 2)
        cuts.append(D); allw = []
        for i in range(len(cuts) - 1):
            mp3 = wav[:-4] + f"_asr{i}.mp3"
            subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{cuts[i]:.3f}","-to",f"{cuts[i+1]:.3f}","-i",wav,"-ac","1","-ar","16000","-b:a","64k",mp3], check=True)
            allw += [{"start": w["start"] + cuts[i], "end": w["end"] + cuts[i], "word": w["word"]} for w in asr(mp3).get("words", [])]
        json.dump({"words": allw, "cuts": cuts}, open(cj, "w", encoding="utf-8"), ensure_ascii=False)
    W = [(w["start"], w["end"], norm(w["word"])) for w in json.load(open(cj, encoding="utf-8")).get("words", [])]
    W = [w for w in W if w[2]]
    M = []                                   # 시각이 거꾸로 가는(받아쓰기 헛소리) 단어는 버린다
    for w in W:
        if not M or (w[0] >= M[-1][0] - 0.05 and w[1] >= w[0]): M.append(w)
    W = M
    # 조각 경계: 대본 글자열과 받아쓰기 글자열을 한 글자씩 맞대어(difflib) 경계 글자가 든 단어를 찾는다
    import difflib
    A = ""; owner = []
    for k, w in enumerate(W): A += w[2]; owner += [k] * len(w[2])
    T = ""; ends = []
    for _, t in texts: T += norm(t); ends.append(len(T))
    sm = difflib.SequenceMatcher(None, T, A, autojunk=False); m = {}
    for a0, b0, n in sm.get_matching_blocks():
        for j in range(n): m[a0 + j] = b0 + j
    def asr_pos(i):                       # 대본 글자 i → 받아쓰기 글자 위치(맞는 글자가 없으면 앞뒤에서 보간)
        lo = next((m[x] for x in range(i, -1, -1) if x in m), 0); hi = next((m[x] for x in range(i, len(T)) if x in m), len(A) - 1)
        return lo if i in m else (lo + hi) / 2
    bounds = []
    for e in ends[:-1]:
        p = asr_pos(e - 1)                # 앞 조각 마지막 글자
        k = owner[min(len(owner) - 1, int(round(p)))]
        tb = W[k][1]; nb = W[k + 1][0] if k + 1 < len(W) else D
        k2 = owner[min(len(owner) - 1, int(round(asr_pos(e))))]
        if k2 == k:                       # 받아쓰기가 두 조각 글자를 한 단어로 묶었다 → 그 단어 안 쉼, 없으면 글자 비율 자리
            w0, w1 = W[k][0], W[k][1]; inside = [(a, b) for a, b in gaps if a > w0 and b < w1 + 0.3]
            if inside: a, b = max(inside, key=lambda g: g[1] - g[0]); bounds.append((a + b) / 2); continue
            ci = [i for i, o in enumerate(owner) if o == k]; r = (int(round(p)) - ci[0] + 1) / len(ci)
            tb = nb = w0 + (w1 - w0) * r
        # 그 단어 끝 ~ 다음 단어 시작 사이 쉼 가운데(쉼이 없으면 그 사이 가운데)
        cand = [(a, b) for a, b in gaps if b > tb - 0.15 and a < nb + 0.15]
        if cand: a, b = max(cand, key=lambda g: g[1] - g[0]); cut = (max(a, tb - 0.15) + min(b, nb + 0.15)) / 2
        else: cut = (tb + nb) / 2
        bounds.append(cut)
    for i in range(1, len(bounds)):            # 경계는 앞으로만
        if bounds[i] < bounds[i - 1] + 0.8: bounds[i] = bounds[i - 1] + 0.8
    edges = [0.0] + bounds + [D]
    return [(edges[i], edges[i + 1]) for i in range(len(texts))], W

def char_times(text, a, b, W):
    """조각 글자마다 시각 — 조각 안 단어 시각을 글자 수 비율로 나눠 붙인다(자막 덩어리용)."""
    ws = [w for w in W if a - 0.05 <= (w[0] + w[1]) / 2 <= b + 0.05]
    n = len(text); st = [0.0] * n; en = [0.0] * n
    if not ws: ws = [(a, b, norm(text))]
    tot = sum(len(w[2]) for w in ws) or 1; idx = [i for i, ch in enumerate(text) if norm(ch)]
    k = 0; done = 0
    for w0, w1, t in ws:
        m = round(len(t) / tot * len(idx)) if (w0, w1, t) != ws[-1] else len(idx) - done
        for j in range(m):
            if done + j >= len(idx): break
            i = idx[done + j]; st[i] = w0 - a + (w1 - w0) * j / max(1, m); en[i] = w0 - a + (w1 - w0) * (j + 1) / max(1, m)
        done += m
    last = 0.0
    for i in range(n):                       # 띄어쓰기·문장부호는 앞 글자 시각을 잇는다
        if not norm(text[i]): st[i] = en[i] = last
        else: last = en[i]
    return st, en

if __name__ == "__main__":
    wav, n0, n1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    items = {q["ni"]: q["text"] for q in json.load(open("items.json", encoding="utf-8")) if q["type"] == "N"}
    texts = [(i, items[i]) for i in range(n0, n1 + 1)]
    segs, W = split(wav, texts); os.makedirs("narr", exist_ok=True)
    for (ni, t), (a, b) in zip(texts, segs):
        st, en = char_times(t, a, b, W)
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{a:.3f}","-to",f"{b:.3f}","-i",wav,"-af","silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000","-ac","2",f"narr/n{ni:03d}.wav"], check=True)
        # 앞 쉼을 잘라냈으니 글자 시각을 앞당긴다
        lead = next((w[0] for w in W if w[0] >= a - 0.05), a) - a
        st = [max(0, x - max(0, lead - 0.05)) for x in st]; en = [max(0, x - max(0, lead - 0.05)) for x in en]
        json.dump({"text": t, "chars": list(t), "st": st, "en": en, "src": [wav, round(a, 3), round(b, 3)]}, open(f"narr/n{ni:03d}.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(ni, f"{a:.2f}-{b:.2f}", round(dur(f"narr/n{ni:03d}.wav"), 2), t[:20], flush=True)
