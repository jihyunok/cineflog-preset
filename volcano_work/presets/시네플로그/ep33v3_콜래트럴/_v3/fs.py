# -*- coding: utf-8 -*-
"""원본(또는 --mp4) 시각들의 프레임을 한 장 시트로.  python fs.py out.jpg t1 t2 ... | out.jpg a:b:step  [--mp4 파일] [--w 400] [--cols 5]"""
import os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
args = sys.argv[1:]; out = args.pop(0)
mp4 = "D:/cine_work/ep33_콜래트럴/src.mp4"; W = 400; C = 5
if "--mp4" in args: i = args.index("--mp4"); mp4 = args[i + 1]; del args[i:i + 2]
if "--w" in args: i = args.index("--w"); W = int(args[i + 1]); del args[i:i + 2]
if "--cols" in args: i = args.index("--cols"); C = int(args[i + 1]); del args[i:i + 2]
ts = []
for a in args:
    if a.count(":") == 2:
        x, y, st = map(float, a.split(":")); t = x
        while t <= y + 1e-6: ts.append(round(t, 2)); t += st
    else: ts.append(float(a))
tmp = tempfile.mkdtemp()
def grab(t):
    p = os.path.join(tmp, f"{t:.2f}.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", mp4, "-frames:v", "1", "-vf", f"scale={W}:-2", p])
    return p
with ThreadPoolExecutor(4) as ex: ps = list(ex.map(grab, ts))
ims = [Image.open(p) for p in ps if os.path.exists(p)]
h = ims[0].height; R = (len(ims) + C - 1) // C
sheet = Image.new("RGB", (C * W, R * (h + 22)), "black"); d = ImageDraw.Draw(sheet)
try: f = ImageFont.truetype("arial.ttf", 18)
except Exception: f = None
for n, (t, im) in enumerate(zip(ts, ims)):
    x, y = (n % C) * W, (n // C) * (h + 22)
    sheet.paste(im, (x, y + 22)); d.text((x + 4, y + 2), f"{t:.1f}  {int(t//60)}:{t%60:04.1f}", fill="yellow", font=f)
sheet.save(out, quality=85); print(out, len(ims))
