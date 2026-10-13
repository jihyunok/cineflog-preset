# -*- coding: utf-8 -*-
"""대본 조각 번호가 밀려도 이미 녹음한 나레를 글자로 찾아 새 번호로 옮긴다(ElevenLabs 크레딧 아끼기). tts02 전에 돈다."""
import json, glob, os, shutil
have = {}
for js in glob.glob("narr*/n*.json"):
    b = js[:-5]
    if os.path.exists(b + ".wav"): have.setdefault(json.load(open(js, encoding="utf-8"))["text"], b)
os.makedirs("narr_pool", exist_ok=True)
pool = {}
for t, b in have.items():
    nb = "narr_pool/" + str(abs(hash(t)))
    for ext in (".json", ".wav", ".mp3"):
        if os.path.exists(b + ext): shutil.copy(b + ext, nb + ext)
    pool[t] = nb
for f in glob.glob("narr/*"): os.remove(f)
os.makedirs("narr", exist_ok=True); n = 0
for q in json.load(open("items.json", encoding="utf-8")):
    if q["type"] == "N" and q["text"] in pool:
        for ext in (".json", ".wav", ".mp3"):
            if os.path.exists(pool[q["text"]] + ext): shutil.copy(pool[q["text"]] + ext, f"narr/n{q['ni']:03d}{ext}")
        n += 1
print("reused", n)
