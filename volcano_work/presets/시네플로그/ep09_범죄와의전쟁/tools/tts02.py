# -*- coding: utf-8 -*-
import base64, json, os, subprocess, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
K = open(os.path.expanduser("~/.volcano/keys/elevenlabs")).read().strip()
VOICE = "DkAJhrMznCtWh38YrjTv"
items = [q for q in json.load(open("items.json", encoding="utf-8")) if q["type"] == "N"]
def one(q):
    i, text = q["ni"], q["text"]
    raw, js, fin = f"narr/n{i:03d}.mp3", f"narr/n{i:03d}.json", f"narr/n{i:03d}.wav"
    if os.path.exists(js) and json.load(open(js, encoding="utf-8")).get("text") == text and os.path.exists(fin): return
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
    json.dump({"text": text, "chars": al["characters"], "st": al["character_start_times_seconds"],
               "en": al["character_end_times_seconds"]}, open(js, "w", encoding="utf-8"), ensure_ascii=False)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000", "-ac", "2", fin], check=True)
    print(i, "ok", flush=True)
with ThreadPoolExecutor(2) as ex:
    list(ex.map(one, items))
print("done")
