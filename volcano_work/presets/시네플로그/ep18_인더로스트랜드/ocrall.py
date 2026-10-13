# 모든 자막 이벤트의 띠 그림을 한 번 훑어 모은다 → ocr/<id>.png, ocr_sheet_NN.png (30줄씩)
import json, subprocess, os
import numpy as np
from PIL import Image, ImageDraw
EV = json.load(open("subev.json"))
want = {}
for e in EV: want.setdefault(e["f"], []).append(e["id"])
W, H = 780, 90
p = subprocess.Popen(["ffmpeg","-v","error","-i","src.mp4","-vf",f"fps=5,crop=1300:150:310:585,scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
os.makedirs("ocr", exist_ok=True); k = 0; last = max(want)
while k <= last:
    b = p.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    if k in want:
        im = Image.frombytes("RGB", (W, H), b)
        for i in want[k]: im.save(f"ocr/{i}.png")
    k += 1
p.kill()
ids = [e["id"] for e in EV]; evd = {e["id"]: e for e in EV}
for s in range(0, len(ids), 30):
    rows = []
    for i in ids[s:s+30]:
        im = Image.open(f"ocr/{i}.png"); c = Image.new("RGB", (900, 90), "black"); c.paste(im, (120, 0))
        e = evd[i]; t = e["s"]
        ImageDraw.Draw(c).text((4, 30), f"{i}\n{int(t//3600)}:{int(t%3600//60):02d}:{t%60:04.1f}", fill="yellow"); rows.append(c)
    S = Image.new("RGB", (900, 90*len(rows)))
    for r, im in enumerate(rows): S.paste(im, (0, r*90))
    S.save(f"ocr_sheet_{s//30:02d}.png")
print("sheets", (len(ids)+29)//30)
