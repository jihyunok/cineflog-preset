# -*- coding: utf-8 -*-
"""원본 영어 대사를 Groq 로 받아써 낱말 시각(src_words.json)을 만든다 — 대사 창을 '자막 OCR 시각(subev)'이 아니라 실제 말소리에 맞추려고.
10-13 "5분4초 고 늦게나와": subev 는 박힌 자막이 뜬 시각이라 말소리와 어긋날 수 있다."""
import json, os, subprocess, time, uuid, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
KEY = open(os.path.expanduser("~/.volcano/keys/groq"), encoding="utf-8").read().strip()
SRC = "../ep16v4_핀치/src.mp4"; SEG = 600; TOT = 6940
def asr(p):
    b = "----x" + uuid.uuid4().hex; parts = []
    for k, v in [("model", "whisper-large-v3"), ("response_format", "verbose_json"), ("temperature", "0"), ("language", "en"), ("timestamp_granularities[]", "word")]:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode())
    parts.append(open(p, "rb").read()); parts.append(f"\r\n--{b}--\r\n".encode())
    for _ in range(30):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=b"".join(parts),
                headers={"Authorization": "Bearer " + KEY, "Content-Type": "multipart/form-data; boundary=" + b, "User-Agent": "curl/8"}), timeout=300))
        except urllib.error.HTTPError as e:
            e.read(); time.sleep(30 if e.code == 429 else 5)
        except Exception: time.sleep(5)
def one(k):
    m = f"_src{k}.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(k * SEG), "-t", str(SEG + 5), "-i", SRC, "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", m], check=True)
    r = asr(m); os.remove(m)
    return [(round(k * SEG + w["start"], 2), round(k * SEG + w["end"], 2), w["word"]) for w in r.get("words", []) if w["start"] < SEG]
with ThreadPoolExecutor(3) as ex: R = list(ex.map(one, range(TOT // SEG + 1)))
W = [w for r in R for w in r]
json.dump(W, open("src_words.json", "w", encoding="utf-8"), ensure_ascii=False)
print("낱말", len(W))
