# -*- coding: utf-8 -*-
"""나레 자막 ↔ 목소리 대조 3판 (10-13). subcheck.py 는 섞인 소리(원본 효과음 깔림)를 받아쓰고 첫 두 글자만 비교해서
'그리고·하지만·핀치' 같은 흔한 첫 낱말을 옆 문장 것과 짝지었다(가짜 어긋남). → 나레만 든 트랙(narr_track8.wav)을 받아쓰고,
자막 줄 앞 두 낱말(공백 없이 6글자까지)이 받아쓴 낱말 이어붙임에서 시작하는 자리만 짝으로 친다. 받아쓴 낱말은 _sc3_words.json 에 남김.
사용: python subcheck3.py narr_track8.wav subs_v8.ass"""
import json, os, re, subprocess, sys, time, uuid, urllib.request, urllib.error
KEY = open(os.path.expanduser("~/.volcano/keys/groq"), encoding="utf-8").read().strip()
V, A = sys.argv[1], sys.argv[2]
CACHE = "_sc3_words.json"
def asr(p):
    b = "----x" + uuid.uuid4().hex; parts = []
    for k, v in [("model", "whisper-large-v3"), ("response_format", "verbose_json"), ("temperature", "0"), ("language", "ko"), ("timestamp_granularities[]", "word")]:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode())
    parts.append(open(p, "rb").read()); parts.append(f"\r\n--{b}--\r\n".encode())
    for _ in range(20):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=b"".join(parts),
                headers={"Authorization": "Bearer " + KEY, "Content-Type": "multipart/form-data; boundary=" + b, "User-Agent": "curl/8"}), timeout=300))
        except urllib.error.HTTPError as e:
            e.read(); time.sleep(30 if e.code == 429 else 5)
def clean(s): return re.sub(r"[^가-힣0-9A-Za-z]", "", s)
if os.path.exists(CACHE) and os.path.getmtime(CACHE) > os.path.getmtime(V):
    W = json.load(open(CACHE, encoding="utf-8"))
else:
    W = []
    D = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", V], capture_output=True, text=True).stdout)
    for k in range(int(D // 120) + 1):      # 2분씩 — 길게 받아쓰면 낱말 시각이 밀린다
        m = f"_sc3_{k}.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(k * 120), "-t", "120", "-i", V, "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", m], check=True)
        for w in (asr(m) or {}).get("words", []): W.append((k * 120 + w["start"], clean(w["word"])))
        os.remove(m)
    json.dump(W, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
def ts(x):
    h, m, s = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
bad = []; n = 0; miss = []
for l in open(A, encoding="utf-8"):
    if not l.startswith("Dialogue") or ",N,," not in l: continue
    f = l.rstrip("\n").split(",", 9); a = ts(f[1]); t = f[9]
    key = clean("".join(t.split(" ")[:2]))[:6]
    if len(key) < 3: continue
    n += 1; c = []
    for i, (wt, ww) in enumerate(W):
        if abs(wt - a) > 3: continue
        cat = "".join(x[1] for x in W[i:i + 4])
        if cat.startswith(key[:4]): c.append(wt)
    if not c: miss.append((round(a, 1), t)); continue
    d = min(c, key=lambda x: abs(x - a)) - a
    if abs(d) > 0.5: bad.append((round(a, 1), round(d, 2), t))
print("나레 자막", n, "· 대조 못 함", len(miss), "· 0.5초 넘게 어긋남", len(bad))
for b in bad: print(" ", b)
print("대조 못 함(앞 15):", miss[:15])
