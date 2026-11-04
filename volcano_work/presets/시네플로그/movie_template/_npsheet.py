# -*- coding: utf-8 -*-
# 관문 ⑨ 걸린 조각(gate pre 출력의 nNNN_wWWW)을 조각 처음·가운데·끝 프레임 + 나레 글 + 그림 설명으로 시트에 → _np_N.jpg (ep05 꼴, 13 라스트버스 10-27: 프레임 3장)
import json, re, subprocess, sys, io
from PIL import Image, ImageDraw, ImageFont
ids = re.findall(r"n(\d{3})_w(\d+)", open(sys.argv[1], encoding="utf-8").read())
W = json.load(open("windows.json", encoding="utf-8")); SH = json.load(open("shots.json", encoding="utf-8"))
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
F = ImageFont.truetype("fonts/Cafe24Dangdanghae.ttf", 22); FS = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 13)
desc = lambda t: next((x.get("desc", "") for x in SH if x["s"] <= t < x["e"]), "")
cells = []
def grab(t):
    png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", "src.mp4", "-frames:v", "1", "-vf", "scale=320:-1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGB")
for n, w in ids:
    x = W[int(w)]; sl = (x["b"] - x["a"]) * 1.05; ts = [x["s"] + 0.12, x["s"] + sl / 2, x["s"] + sl - 0.12]; t = ts[1]
    c = Image.new("RGB", (960, 134 + 92), (20, 20, 20))
    for i, tt in enumerate(ts): c.paste(grab(tt), (i * 320, 0))
    d = ImageDraw.Draw(c); txt = S[x["k"]][1]
    d.text((6, 138), f"n{n} w{w} 원본 {x['s']:.1f}~{x['s'] + sl:.1f}", fill=(255, 220, 0), font=FS)
    for i in range(0, min(len(txt), 84), 42): d.text((6, 154 + i // 42 * 24), txt[i:i + 42], fill=(255, 255, 255), font=F)
    d.text((6, 208), desc(t)[:130], fill=(160, 200, 255), font=FS); cells.append(c)
for p in range(0, len(cells), 10):
    sh = Image.new("RGB", (960 * 2, 226 * 5), (0, 0, 0))
    for i, c in enumerate(cells[p:p + 10]): sh.paste(c, (i % 2 * 960, i // 2 * 226))
    sh.save(f"_np_{p // 10}.jpg", quality=80)
print(len(cells), "조각 시트", (len(cells) + 9) // 10)
