import json, ep17, os, subprocess
from PIL import Image, ImageDraw, ImageFont
EV = json.load(open("subev.json")); EVD = {e["id"]: e for e in EV}
NEED = json.load(open("need.json")); KO = json.load(open("ko17.json", encoding="utf-8"))
IT = json.load(open("items.json", encoding="utf-8"))
D = [q for q in IT if q["type"] == "D"]
used = {q["i"] for q in D}
END = 4895
def free(e, extra):
    s, d = e["s"] - 0.05, max(e["e"] - e["s"] + 0.15, 1.0); d = min(d, 3.9 if d > 2.9 else 2.9)
    return all(s + d + 3.0 <= p["s"] or s >= p["s"] + p["d"] + 3.0 for p in D + extra)
F = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
rows = []; out = {}; bi = 0; taken = []
for x in ep17.S:
    if x[0] == "R" or not x[0]: continue
    bi += 1
    if x[1] is None: continue
    ts = [EVD[NEED[str(d)]]["s"] for d in x[1] if not isinstance(d, tuple) and str(d) in NEED]
    if not ts: continue
    a, b = min(ts) - 25, max(ts) + 25
    c = [e for e in EV if a <= e["s"] <= b and e["s"] < END and e["id"] not in used and str(e["id"]) not in KO and free(e, [])]
    if not c: continue
    out[bi] = [e["id"] for e in c]
    for e in c:
        p = f"ocr/{e['id']}.png"
        if not os.path.exists(p):
            subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{(e['s']+e['e'])/2:.2f}","-i","src.mp4","-frames:v","1","-vf","crop=1700:150:110:640,scale=1020:90",p])
        im = Image.new("RGB", (1200, 90), "black"); im.paste(Image.open(p).convert("RGB"), (180, 0))
        ImageDraw.Draw(im).text((4, 20), f"N{bi} e{e['id']}\n{e['s']:.1f}", fill="yellow", font=F); rows.append(im)
json.dump(out, open("cand.json", "w"), indent=0)
os.makedirs("cs", exist_ok=True)
for f in os.listdir("cs"): os.remove("cs/" + f)
for k in range(0, len(rows), 24):
    S = Image.new("RGB", (1200, 90 * len(rows[k:k+24])))
    for r, im in enumerate(rows[k:k+24]): S.paste(im, (0, r * 90))
    S.save(f"cs/c{k//24:02d}.png")
print("blocks", len(out), "cands", len(rows), "sheets", (len(rows)+23)//24)
