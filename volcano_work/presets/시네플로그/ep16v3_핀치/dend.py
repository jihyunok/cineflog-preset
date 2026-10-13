# -*- coding: utf-8 -*-
"""대사가 실제로 끝나는 시각 재기 — 박힌 자막은 말보다 오래 떠 있어서, 자막 길이로 자르면 4초가 넘는 줄이 많다.
대본(ep16v3.S)에서 고른 대사 중 자막 길이 2.9초 넘는 것만 [시작-0.3, 시작+7] 소리를 Groq 단어 시각으로 받아써
다음 자막 시작 전의 마지막 단어 끝을 dend.json 에 적는다. build16v3 plan 이 읽는다."""
import json, os, subprocess, time, uuid, urllib.request, urllib.error, importlib
KEY = open(os.path.expanduser("~/.volcano/keys/groq"), encoding="utf-8").read().strip()
def asr(p):
    b = "----x" + uuid.uuid4().hex; parts = []
    for k, v in [("model", "whisper-large-v3"), ("response_format", "verbose_json"), ("temperature", "0"), ("language", "en"), ("timestamp_granularities[]", "word")]:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode()); parts.append(open(p, "rb").read()); parts.append(f"\r\n--{b}--\r\n".encode())
    while True:
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=b"".join(parts), headers={"Authorization": "Bearer " + KEY, "Content-Type": "multipart/form-data; boundary=" + b, "User-Agent": "curl/8"}), timeout=120))
        except urllib.error.HTTPError as e:
            print("  ", e.code, e.read().decode()[:150], flush=True)
            if e.code in (429, 500, 502, 503): time.sleep(30); continue
            raise
EVL = json.load(open("subev.json")); EV = {e["id"]: e for e in EVL}
EP = importlib.import_module("ep16v3")
ids = [x[1] for x in EP.S if x[0] == "D" and EV[x[1]]["e"] - EV[x[1]]["s"] + 0.2 > 2.95]
out = json.load(open("dend.json")) if os.path.exists("dend.json") else {}
os.makedirs("dend", exist_ok=True)
for i in ids:
    if str(i) in out: continue
    e = EV[i]; nxt = min([x["s"] for x in EVL if x["s"] > e["s"] + 0.2] + [e["s"] + 7])
    a = e["s"] - 0.3; p = f"dend/{i}.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.2f}", "-t", "7.3", "-i", "src.mp4", "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k", p], check=True)
    ws = asr(p).get("words", [])
    ends = [a + w["end"] for w in ws if a + w["start"] < min(nxt, e["e"] + 0.5) - 0.05]
    out[str(i)] = round(max(ends), 2) if ends else None
    print(i, round(e["e"] - e["s"], 2), "→ 말 끝", round(out[str(i)] - e["s"], 2) if ends else None, [w["word"] for w in ws][:12], flush=True)
    json.dump(out, open("dend.json", "w"), indent=0)
