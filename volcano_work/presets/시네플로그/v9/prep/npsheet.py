# -*- coding: utf-8 -*-
# (prep/npsheet.py, 05v2 10-18 — 작업 폴더에서, gate.py pre 결과 _gate_pre.log 필요) 관문 ⑨(제브 나레↔그림 어긋남) 조각을 실제 프레임으로 — 칸마다 나레 글 + 조각 가운데 프레임(완성본처럼 반전). 10-18 05v2
import json, os, re, subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
CFG = json.load(open("ep.json", encoding="utf-8")); SRC = CFG["src"]
W = json.load(open("windows.json", encoding="utf-8"))
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
N = [x[1] for x in ns["S"] if x[0] == "N"]
F = [(int(m.group(1)), int(m.group(2))) for m in re.finditer(r"⑨ 나레↔그림 어긋남 n(\d+)_w(\d+)_", open("_gate_pre.log", encoding="utf-8").read())]
os.makedirs("_np", exist_ok=True)
def frame(nw):
    n, w = nw; x = W[w]; t = x["s"] + (x["b"] - x["a"]) * 1.05 / 2; p = f"_np/{n:03d}_{w}.jpg"
    vf = "scale=400:-2" + ("" if x.get("noflip") else ",hflip")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", SRC, "-frames:v", "1", "-vf", vf, p], check=True)
    return p, n, w, t
with ThreadPoolExecutor(8) as ex: R = list(ex.map(frame, F))
font = ImageFont.truetype("fonts/Cafe24Dangdanghae.ttf", 17)
C, CW, CH = 4, 400, 200 + 50
for s in range(0, len(R), 16):
    part = R[s:s + 16]; rows = (len(part) + C - 1) // C
    im = Image.new("RGB", (C * CW, rows * CH), (20, 20, 20)); d = ImageDraw.Draw(im)
    for i, (p, n, w, t) in enumerate(part):
        x0, y0 = (i % C) * CW, (i // C) * CH
        im.paste(Image.open(p), (x0, y0 + 50))
        txt = f"n{n:03d} w{w} {int(t // 60)}:{t % 60:04.1f}  " + N[n - 1]
        d.text((x0 + 4, y0 + 2), txt[:30], font=font, fill=(255, 255, 0)); d.text((x0 + 4, y0 + 24), txt[30:60], font=font, fill=(255, 255, 0))
    im.save(f"npsheet_{s // 16}.jpg", quality=85)
print(len(R), "조각 ·", (len(R) + 15) // 16, "장")
