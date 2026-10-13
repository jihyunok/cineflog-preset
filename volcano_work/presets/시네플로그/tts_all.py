# -*- coding: utf-8 -*-
"""episode.py 의 N 블록을 ElevenLabs(Minjun, eleven_v3)로 합성 + 글자 시각 → 1.0배."""
import base64, json, os, subprocess, sys, time, urllib.request, urllib.error
import episode
K = open(os.path.expanduser("~/.volcano/keys/elevenlabs")).read().strip()
VOICE = "DkAJhrMznCtWh38YrjTv"
TEMPO = 1.0
os.makedirs("narr", exist_ok=True)
ns = [b for b in episode.BLOCKS if b[0] == "N"]
for i, b in enumerate(ns, 1):
    text = b[1]
    raw, js, fin = f"narr/n{i:02d}.mp3", f"narr/n{i:02d}.json", f"narr/n{i:02d}.wav"
    if os.path.exists(js) and json.load(open(js, encoding="utf-8")).get("text") == text and os.path.exists(fin):
        continue
    body = json.dumps({"text": text, "model_id": "eleven_v3",
                       "voice_settings": {"stability": 0.5, "similarity_boost": 0.71}}, ensure_ascii=False).encode("utf-8")
    for tries in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(
                f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",
                data=body, headers={"xi-api-key": K, "Content-Type": "application/json"}), timeout=300)
            d = json.load(r); break
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:300]; print(i, e.code, msg, flush=True)
            if e.code in (429, 500, 502, 503): time.sleep(20); continue
            sys.exit(1)
    open(raw, "wb").write(base64.b64decode(d["audio_base64"]))
    al = d.get("alignment") or d.get("normalized_alignment")
    json.dump({"text": text, "chars": al["characters"],
               "st": [x / TEMPO for x in al["character_start_times_seconds"]],
               "en": [x / TEMPO for x in al["character_end_times_seconds"]]},
              open(js, "w", encoding="utf-8"), ensure_ascii=False)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                    f"atempo={TEMPO},loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000", "-ac", "2", fin], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", fin],
                               capture_output=True, text=True).stdout)
    print(f"n{i:02d} {dur:5.1f}s {len(text)}자", flush=True)
