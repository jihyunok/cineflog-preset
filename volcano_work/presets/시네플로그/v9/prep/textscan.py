# -*- coding: utf-8 -*-
"""반전하면 거꾸로 보일 글자 조각 후보 — 조각마다 agy 그림 설명에 글자·화면 낱말이 있으면 프레임을 뽑아 한 장 시트로.
(강의: 글자·간판 크게 나오는 컷은 좌우반전 금지 / 17 그레이하운드 「반전 조각을 전부 크게 뽑아 훑어」)
사용: python textscan.py [windows_dry.json] → textscan.txt · textscan_*.jpg (번호·대본 줄·종류 표시)"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw
W = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "windows_dry.json", encoding="utf-8"))
S = json.load(open("shots.json", encoding="utf-8")); CFG = json.load(open("ep.json", encoding="utf-8"))
KW = re.compile(r"\b(text|sign|signs|screen|monitor|news|television|TV|logo|letters|reading|card|map|whiteboard|billboard|title|newspaper|poster|label|words|headline|subtitle|caption|banner|computer|tablet|laptop|phone)\b", re.I)
def desc(t): return next((x for x in S if x["s"] <= t < x["e"]), {}).get("desc", "")
rows = []
for j, w in enumerate(W):
    if w.get("noflip"): continue
    sl = (w["b"] - w["a"]) * (w.get("rate", 1.05 if w["kind"] == "A" else 1.0))
    d = desc(w["s"] + sl / 2)
    if KW.search(d): rows.append((j, w, d))
open("textscan.txt", "w", encoding="utf-8").write("\n".join(f"{j}\t줄{w['k']}\t{w['kind']}\t{w['s']:.1f}\t{d}" for j, w, d in rows) + "\n")
os.makedirs("_ts", exist_ok=True); tiles = []
for j, w, d in rows:
    p = f"_ts/{j}.jpg"
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{w['s'] + 0.6:.2f}", "-i", CFG["src"], "-frames:v", "1", "-vf", "scale=320:-2", p])
    im = Image.open(p).convert("RGB"); ImageDraw.Draw(im).rectangle([0, 0, 130, 16], fill=(0, 0, 0)); ImageDraw.Draw(im).text((3, 2), f"#{j} 줄{w['k']} {w['kind']}", fill=(255, 255, 0)); tiles.append(im)
for b in range(0, len(tiles), 30):
    T = tiles[b:b + 30]; w0, h0 = T[0].size; sh = Image.new("RGB", (w0 * 6, h0 * ((len(T) + 5) // 6)))
    for i, im in enumerate(T): sh.paste(im, ((i % 6) * w0, (i // 6) * h0))
    sh.save(f"textscan_{b // 30}.jpg", quality=85)
print("후보", len(rows), "· 시트", (len(tiles) + 29) // 30)
