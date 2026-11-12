# -*- coding: utf-8 -*-
"""이름표 미리 보기(10-22 B판부터 — 조각 자르기 전에): script.py 의 이름표 줄마다 windows(.json 또는 _dry) 에서 그 줄의 조각(tag_w 번째)을 찾아
원본 가운데 프레임(반전 조각이면 좌우 뒤집어)에 이름을 적어 시트로 → _tagsheet.jpg. 인물이 혼자 크게 보이는지 눈으로 본다.
사용: python _tagsheet.py [windows.json]"""
import json, subprocess, sys, io, os
from PIL import Image, ImageDraw, ImageFont
WF = sys.argv[1] if len(sys.argv) > 1 else ("windows.json" if os.path.exists("windows.json") else "windows_dry.json")
W = json.load(open(WF, encoding="utf-8")); ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
SRC = json.load(open("ep.json", encoding="utf-8"))["src"]
F = ImageFont.truetype("fonts/Cafe24Dangdanghae.ttf", 26)
cells = []
for k, x in enumerate(S):
    o = x[-1] if isinstance(x[-1], dict) else {}
    if not o.get("tag"): continue
    ws = [w for w in W if w["k"] == k]
    if not ws: continue
    w = ws[min(o.get("tag_w", 0), len(ws) - 1)]; t = w["s"] + (w["b"] - w["a"]) / 2
    vf = "scale=480:-1" + ("" if o.get("noflip") else ",hflip")
    png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", SRC, "-frames:v", "1", "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    im = Image.open(io.BytesIO(png)).convert("RGB"); c = Image.new("RGB", (480, im.height + 40), (20, 20, 20)); c.paste(im, (0, 0))
    tg = o["tag"] if isinstance(o["tag"], str) else " / ".join(o["tag"])
    ImageDraw.Draw(c).text((6, im.height + 6), f"S{k} {tg} ({t:.0f}s)", fill=(255, 220, 0), font=F); cells.append(c)
if cells:
    cols = 4; h = cells[0].height; sh = Image.new("RGB", (480 * cols, h * ((len(cells) + cols - 1) // cols)))
    for i, c in enumerate(cells): sh.paste(c, (480 * (i % cols), h * (i // cols)))
    sh.save("_tagsheet.jpg", quality=85)
print("이름표", len(cells), "→ _tagsheet.jpg")
