# -*- coding: utf-8 -*-
"""벤치 화면 vs 우리 창 원본 화면 나란히(지정 구간, 3초마다). 사용: python cmp_sheet.py windows_v8.json 135 240 out.jpg"""
import json, subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
W = json.load(open(sys.argv[1], encoding="utf-8")); t0, t1, out = float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
BENCH = sys.argv[5] if len(sys.argv) > 5 else "bench/bench.mp4"
PL = json.load(open("narr_place.json"))
def grab(p, t):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", p, "-frames:v", "1", "-vf", "scale=320:180", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return Image.frombytes("RGB", (320, 180), b) if len(b) == 320 * 180 * 3 else Image.new("RGB", (320, 180))
ts = list(np.arange(t0, t1, 3.0)); cols = 3; rows = (len(ts) + cols - 1) // cols
sh = Image.new("RGB", (cols * 660, rows * 200), "white"); d = ImageDraw.Draw(sh)
f = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 14)
for i, t in enumerate(ts):
    w = next(w for w in W if w["a"] <= t < w["b"]); sp = w.get("rate", 1.05) if w["kind"] == "A" else 1
    x, y = (i % cols) * 660, (i // cols) * 200
    sh.paste(grab(BENCH, t), (x, y)); sh.paste(grab("../ep16v4_핀치/src.mp4", w["s"] + (t - w["a"]) * sp), (x + 322, y))
    n = "N" if any(q["t"] <= t < q["t"] + q["d"] for q in PL) else "-"
    d.text((x + 2, y + 181), f"{int(t//60)}:{t%60:04.1f} {w['kind']}{n} 원본{w['s']:.0f}", fill="black", font=f)
sh.save(out, quality=80); print(out)
