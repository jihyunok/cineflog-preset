import json, ep17, os, subprocess
from PIL import Image, ImageDraw, ImageFont
EN = json.load(open("en.json", encoding="utf-8")); EV = {e["id"]: e for e in json.load(open("subev.json"))}
NEED = json.load(open("need.json"))
F = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
ds = []
for x in ep17.S:
    if x[0] == "R" or x[1] is None: continue
    for d in x[1]:
        if not isinstance(d, tuple): ds.append(d)
rows = []
for d in ds:
    eid = NEED[str(d)]; e = EV[eid]; p = f"ocr/{eid}.png"
    if not os.path.exists(p):
        t = (e["s"] + e["e"]) / 2
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{t:.2f}","-i","src.mp4","-frames:v","1","-vf","crop=1700:150:110:640,scale=1020:90",p])
    c = Image.new("RGB", (1540, 90), "black"); c.paste(Image.open(p).convert("RGB"), (520, 0))
    dr = ImageDraw.Draw(c); dt = e["s"] - EN[d-1]["s"]
    dr.text((4, 4), f"d{d} e{eid} {e['s']:.1f}s dt{dt:+.1f}", fill="yellow", font=F)
    txt = EN[d-1]["t"]; dr.text((4, 30), txt[:60], fill="white", font=F); dr.text((4, 52), txt[60:120], fill="white", font=F)
    rows.append(c)
os.makedirs("vs", exist_ok=True)
for k in range(0, len(rows), 25):
    S = Image.new("RGB", (1540, 90 * len(rows[k:k+25])))
    for r, im in enumerate(rows[k:k+25]): S.paste(im, (0, r * 90))
    S.save(f"vs/v{k//25:02d}.png")
print(len(rows), (len(rows)+24)//25)
