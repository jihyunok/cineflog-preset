import json, ep07, subprocess, os
from PIL import Image, ImageDraw
EN = json.load(open("en.json", encoding="utf-8")); EV = json.load(open("subev.json"))
def ev_for(i):
    s = EN[i - 1]["s"]
    cand = [e for e in EV if e["s"] - 1.0 <= s <= e["e"] + 0.3]
    if not cand: cand = sorted(EV, key=lambda e: abs(e["s"] - s))[:1]
    return min(cand, key=lambda e: abs(e["s"] - s))
need = {}; miss = []
for x in ep07.S:
    if x[0] == "R" or x[1] is None: continue
    for d in x[1]:
        if isinstance(d, tuple): continue
        e = ev_for(d)
        if abs(e["s"] - EN[d - 1]["s"]) > 2.5: miss.append((d, EN[d-1]["s"], e["s"]))
        need[d] = e["id"]
json.dump(need, open("need.json", "w"))
ids = sorted(set(need.values()))
print("대사", len(need), "이벤트", len(ids), "멀리 떨어짐", len(miss), miss[:10])
os.makedirs("ocr", exist_ok=True)
evd = {e["id"]: e for e in EV}
for k in range(0, len(ids), 30):
    rows = []
    for i in ids[k:k+30]:
        e = evd[i]; t = (e["s"] + e["e"]) / 2; p = f"ocr/{i}.png"
        if not os.path.exists(p):
            subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{t:.2f}","-i","src.mp4","-frames:v","1","-vf","crop=1300:150:310:645,scale=780:90",p])
        im = Image.open(p).convert("RGB"); c = Image.new("RGB", (880, 90), "black"); c.paste(im, (100, 0))
        ImageDraw.Draw(c).text((6, 35), str(i), fill="yellow"); rows.append(c)
    S = Image.new("RGB", (880, 90 * len(rows)))
    for r, im in enumerate(rows): S.paste(im, (0, r * 90))
    S.save(f"ocr_sheet_{k//30:02d}.png")
print("sheets", (len(ids) + 29) // 30)
