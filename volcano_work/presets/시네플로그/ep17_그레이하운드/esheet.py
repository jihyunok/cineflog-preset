import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
EV = {e["id"]: e for e in json.load(open("subev.json"))}
F = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
ids = []
for a in sys.argv[2:]:
    if "-" in a: x, y = map(int, a.split("-")); ids += list(range(x, y + 1))
    else: ids.append(int(a))
rows = []
for eid in ids:
    e = EV[eid]; p = f"ocr/{eid}.png"
    if not os.path.exists(p):
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{(e['s']+e['e'])/2:.2f}","-i","src.mp4","-frames:v","1","-vf","crop=1700:150:110:640,scale=1020:90",p])
    c = Image.new("RGB", (1200, 90), "black"); c.paste(Image.open(p).convert("RGB"), (180, 0))
    ImageDraw.Draw(c).text((4, 30), f"e{eid} {e['s']:.1f}", fill="yellow", font=F); rows.append(c)
S = Image.new("RGB", (1200, 90 * len(rows)))
for r, im in enumerate(rows): S.paste(im, (0, r * 90))
S.save(sys.argv[1])
