# -*- coding: utf-8 -*-
"""새로 넣은 줄(script_pre_extend.py 에 없던 줄)의 화면을 final.mp4 에서 뽑아 글과 나란히 — 눈으로 확인용 시트.
사용(작업 폴더에서): py -3.12 review_new.py 출력폴더"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
def load(p):
    ns = {}; exec(open(p, encoding="utf-8").read(), ns); return ns["S"]
S = load("script.py"); OLD = {repr(x) for x in load("script_pre_extend.py")}
newk = {k for k, x in enumerate(S) if x[0] != "ZONE" and repr(x) not in OLD}
W = json.load(open("windows.json", encoding="utf-8"))
F = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 22)
rows = []
for w in W:
    if w["k"] not in newk: continue
    x = S[w["k"]]; lab = x[1] if x[0] == "N" else (w.get("ko", "") if x[0] == "D" else "A")
    t = (w["a"] + w["b"]) / 2
    rows.append((t, f"{int(t // 60)}:{t % 60:04.1f} {x[0]} {lab}"))
ims = []
for t, lab in rows:
    p = f"{OUT}/_f.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", "final.mp4", "-frames:v", "1", "-vf", "scale=480:-2", p], check=True)
    im = Image.open(p).convert("RGB"); c = Image.new("RGB", (480, 270 + 56), "black"); c.paste(im, (0, 0))
    d = ImageDraw.Draw(c); d.text((4, 272), lab[:30], font=F, fill="yellow"); d.text((4, 298), lab[30:62], font=F, fill="yellow"); ims.append(c)
for s in range(0, len(ims), 16):
    part = ims[s:s + 16]; m = Image.new("RGB", (480 * 4, 326 * ((len(part) + 3) // 4)))
    for k, im in enumerate(part): m.paste(im, ((k % 4) * 480, (k // 4) * 326))
    m.save(f"{OUT}/new_{s // 16:02d}.jpg", quality=85)
print(len(rows), "조각 ·", (len(ims) + 15) // 16, "장")
