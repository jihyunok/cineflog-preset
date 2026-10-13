# 나레 조각 번호가 밀렸을 때 이미 만든 음성을 글자로 찾아 새 번호로 옮긴다(다시 녹음 안 하게)
import json, glob, os, shutil
old = {}
for js in glob.glob("narr/n*.json"):
    b = js[:-5]; old[json.load(open(js, encoding="utf-8"))["text"]] = b
os.makedirs("narr_tmp", exist_ok=True)
for b in set(old.values()):
    for ext in (".json", ".wav", ".mp3"):
        if os.path.exists(b + ext): shutil.move(b + ext, "narr_tmp/" + os.path.basename(b) + ext)
n = 0
for q in json.load(open("items.json", encoding="utf-8")):
    if q["type"] != "N" or q["text"] not in old: continue
    src = "narr_tmp/" + os.path.basename(old[q["text"]]); dst = f"narr/n{q['ni']:03d}"
    for ext in (".json", ".wav", ".mp3"):
        if os.path.exists(src + ext): shutil.move(src + ext, dst + ext)
    n += 1
print("옮김", n, "남은", len(os.listdir("narr_tmp")))
