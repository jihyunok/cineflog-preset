# 이름표 옮길 후보: 줄 S 번호 주변(±R) 줄마다 조각 가운데 프레임(반전 반영) → _tagcand_<S>.jpg
import json, subprocess, io, sys
from PIL import Image, ImageDraw, ImageFont
W = json.load(open("windows.json", encoding="utf-8")); ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
F = ImageFont.truetype("fonts/Cafe24Dangdanghae.ttf", 22)
for arg in sys.argv[1:]:
    k0, lo, hi = [int(x) for x in arg.split(":")]
    cells = []
    for k in range(lo, hi + 1):
        x = S[k]
        if x[0] == "ZONE": continue
        o = x[-1] if isinstance(x[-1], dict) else {}
        for j, w in enumerate([w for w in W if w["k"] == k]):
            t = w["s"] + (w["b"] - w["a"]) / 2
            vf = "scale=320:-1" + ("" if o.get("noflip") else ",hflip")
            png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", "src.mp4", "-frames:v", "1", "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
            im = Image.open(io.BytesIO(png)).convert("RGB"); c = Image.new("RGB", (320, im.height + 30), (20, 20, 20)); c.paste(im, (0, 0))
            ImageDraw.Draw(c).text((4, im.height + 2), f"S{k} {x[0]} w{j} {t:.0f}s", fill=(255, 220, 0), font=F); cells.append(c)
    cols = 5; h = cells[0].height
    sh = Image.new("RGB", (320 * cols, h * ((len(cells) + cols - 1) // cols)))
    for i, c in enumerate(cells): sh.paste(c, (i % cols * 320, i // cols * h))
    sh.save(f"_tagcand_{k0}.jpg", quality=75); print(k0, len(cells))
