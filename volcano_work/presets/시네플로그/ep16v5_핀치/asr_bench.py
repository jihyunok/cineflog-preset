# -*- coding: utf-8 -*-
"""벤치 영상 한국어 받아쓰기(Groq whisper-large-v3, 낱말 시간) → bench/asr.json"""
import json, os, subprocess, time, uuid, urllib.request, urllib.error
KEY = open(os.path.expanduser("~/.volcano/keys/groq"), encoding="utf-8").read().strip()
def asr(p):
    b = "----x" + uuid.uuid4().hex; parts = []
    for k, v in [("model", "whisper-large-v3"), ("response_format", "verbose_json"), ("temperature", "0"), ("language", "ko"),
                 ("timestamp_granularities[]", "segment"), ("timestamp_granularities[]", "word")]:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode())
    parts.append(open(p, "rb").read()); parts.append(f"\r\n--{b}--\r\n".encode())
    while True:
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=b"".join(parts),
                headers={"Authorization": "Bearer " + KEY, "Content-Type": "multipart/form-data; boundary=" + b, "User-Agent": "curl/8"}), timeout=300))
        except urllib.error.HTTPError as e:
            m = e.read().decode()[:200]; print("  ", e.code, m, flush=True)
            if e.code == 429: time.sleep(40); continue
            raise
os.makedirs("bench/asr", exist_ok=True)
segs = []; words = []
for k in range(3):
    j = f"bench/asr/{k:02d}.json"
    if not os.path.exists(j):
        p = f"bench/asr/{k:02d}.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(k * 600), "-t", "600", "-i", "bench/bench.mp4", "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", p], check=True)
        json.dump(asr(p), open(j, "w", encoding="utf-8"), ensure_ascii=False); print(k, "ok", flush=True)
    r = json.load(open(j, encoding="utf-8"))
    for s in r["segments"]: segs.append({"s": round(k * 600 + s["start"], 2), "e": round(k * 600 + s["end"], 2), "t": s["text"].strip()})
    for w in r.get("words", []): words.append({"s": round(k * 600 + w["start"], 2), "e": round(k * 600 + w["end"], 2), "w": w["word"]})
json.dump({"segments": segs, "words": words}, open("bench/asr.json", "w", encoding="utf-8"), ensure_ascii=False)
print("segments", len(segs), "words", len(words))
