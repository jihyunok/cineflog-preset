# -*- coding: utf-8 -*-
"""완성본 소리를 10분씩 받아써서(Groq 낱말 시각) 나레 자막 줄마다 첫 낱말이 실제로 들리는 시각과 비교. 0.5초 넘게 어긋난 줄을 찍는다.
사용: python subcheck.py 영상.mp4 자막.ass"""
import json, os, re, subprocess, sys, time, uuid, urllib.request, urllib.error
KEY = open(os.path.expanduser("~/.volcano/keys/groq"), encoding="utf-8").read().strip()
V, A = sys.argv[1], sys.argv[2]
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
W = []
D = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", V], capture_output=True, text=True).stdout)
for k in range(int(D // 300) + 1):
    m = f"_chk{k}.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(k * 300), "-t", "300", "-i", V, "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", m], check=True)
    for w in asr(m).get("words", []): W.append((k * 300 + w["start"], re.sub(r"[^가-힣0-9A-Za-z]", "", w["word"])))
    os.remove(m)
def ts(x):
    h, m, s = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
bad = []; n = 0; miss = 0
for l in open(A, encoding="utf-8"):
    if not l.startswith("Dialogue") or ",N,," not in l: continue
    f = l.rstrip("\n").split(",", 9); a = ts(f[1]); t = f[9]
    first = re.sub(r"[^가-힣0-9A-Za-z]", "", t.split(" ")[0])[:2]
    if len(first) < 2: continue
    c = [wt for wt, ww in W if abs(wt - a) < 3 and ww.startswith(first)]
    n += 1
    if not c: miss += 1; continue
    d = min(c, key=lambda x: abs(x - a)) - a
    if abs(d) > 0.5: bad.append((round(a, 1), round(d, 2), t))
print("나레 자막", n, "· 대조 못 함", miss, "· 0.5초 넘게 어긋남", len(bad))
for b in bad[:40]: print(" ", b)
