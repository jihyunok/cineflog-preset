# -*- coding: utf-8 -*-
"""반전 조각 전수 시트 — 좌우반전(noflip 아닌) 조각마다 가운데 프레임을 거꾸로 뒤집어 6x6 시트로. 거꾸로 보이는 글자(간판·차 글씨·화면 글자)를 눈으로 찾는다.
(04v2 10-16: textscan·공식 자막 글자 카드만으로는 소품 글씨를 못 잡았다 — 1판 6:45 견인차 「ROADSIDE WRECKERS」 거꾸로 → 반전 조각 전부를 뒤집어 훑어 12줄 noflip.)
사용: python flipsheet.py [windows.json] → _fs/NNN.jpg · flipsheet_KK.jpg (칸 위 「#조각 줄k 원본초」)"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageOps
W = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "windows.json", encoding="utf-8"))
CFG = json.load(open("ep.json", encoding="utf-8"))
rows = [(j, w) for j, w in enumerate(W) if not w.get("noflip")]
os.makedirs("_fs", exist_ok=True)
def grab(jw):
    j, w = jw
    sl = (w["b"] - w["a"]) * (w.get("rate", 1.05 if w["kind"] == "A" else 1.0))
    p = f"_fs/{w['s'] + sl / 2:.2f}.jpg"       # 10-17 20편: 번호로 저장하면 windows.json 이 바뀐 뒤 옛 그림이 남는다 → 원본 초로
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{w['s'] + sl / 2:.2f}", "-i", CFG["src"], "-frames:v", "1", "-vf", "scale=300:-2", p])
    return p
with ThreadPoolExecutor(6) as ex: paths = list(ex.map(grab, rows))
tiles = []
for (j, w), p in zip(rows, paths):
    im = ImageOps.mirror(Image.open(p).convert("RGB")); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 150, 14], fill=(0, 0, 0)); d.text((3, 1), f"#{j} k{w['k']} {w['kind']} {w['s']:.0f}", fill=(255, 255, 0)); tiles.append(im)
for b in range(0, len(tiles), 36):
    T = tiles[b:b + 36]; w0, h0 = T[0].size; sh = Image.new("RGB", (w0 * 6, h0 * ((len(T) + 5) // 6)))
    for i, im in enumerate(T): sh.paste(im, ((i % 6) * w0, (i // 6) * h0))
    sh.save(f"flipsheet_{b // 36:02d}.jpg", quality=82)
print("반전 조각", len(rows), "· 시트", (len(tiles) + 35) // 36)
