# -*- coding: utf-8 -*-
"""작업 폴더 windows.json 에서 고른 대본 줄 k 의 조각마다 원본 프레임(시작+0.1·가운데) 시트. python kpieces.py out.jpg k1 k2 …"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
WK = r"D:\cine_work\ep31v2_잭리처"; SRC = "D:/cine_work/ep31_잭리처/src.mp4"
out = sys.argv[1]; KS = [int(a) for a in sys.argv[2:]]
ns = {}; exec(open(os.path.join(WK, "script.py"), encoding="utf-8").read(), ns); S = ns["S"]
W = json.load(open(os.path.join(WK, "windows.json"), encoding="utf-8"))
rows = [(k, w) for k in KS for w in W if w["k"] == k]
tmp = tempfile.mkdtemp(); FW = 300
def grab(t):
    p = os.path.join(tmp, f"{t:.2f}.jpg")
    if not os.path.exists(p): subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", SRC, "-frames:v", "1", "-vf", f"scale={FW}:-2" + (",hflip" if False else ""), p])
    return p
ts = [t for k, w in rows for t in (w["s"] + 0.1, w["s"] + (w["b"] - w["a"]) / 2)]
with ThreadPoolExecutor(3) as ex: list(ex.map(grab, ts))
F = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 15)
h = Image.open(os.path.join(tmp, f"{ts[0]:.2f}.jpg")).height; C = 2
cell = h + 40; sheet = Image.new("RGB", (FW * 4 + 12, cell * ((len(rows) + 1) // 2)), "black"); d = ImageDraw.Draw(sheet)
for i, (k, w) in enumerate(rows):
    x0 = (i % 2) * (FW * 2 + 12); y = (i // 2) * cell
    d.text((x0 + 3, y + 1), f"k{k} 화면 {w['a']:.1f} 원본 {w['s']:.1f}+{w['b']-w['a']:.2f} {'반전' if not w.get('noflip') else ''}", fill="yellow", font=F)
    d.text((x0 + 3, y + 19), S[k][1][:44], fill="white", font=F)
    for c, t in enumerate((w["s"] + 0.1, w["s"] + (w["b"] - w["a"]) / 2)):
        p = os.path.join(tmp, f"{t:.2f}.jpg")
        if os.path.exists(p): sheet.paste(Image.open(p), (x0 + c * FW, y + 40))
sheet.save(out, quality=85); print(out, len(rows))
