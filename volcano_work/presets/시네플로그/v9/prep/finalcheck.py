# -*- coding: utf-8 -*-
"""완성본 건네기 전 검사 — ① 소리 빈 틈(마, 2.5초+ -40dB) ② 까만 화면(0.5초+) ③ 화면 멈춤(1초+) ④ 끝 검은 화면 ⑤ 20초마다 프레임 시트(박힌 자막·로고·거꾸로 글자 눈으로).
사용: python finalcheck.py final.mp4 → finalcheck.txt · finalcheck_*.jpg"""
import re, subprocess, sys
from PIL import Image, ImageDraw
V = sys.argv[1]
def run(args): return subprocess.run(["ffmpeg", "-hide_banner", "-i", V] + args + ["-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", V], capture_output=True, text=True).stdout)
out = [f"길이 {int(dur // 60)}:{dur % 60:04.1f}"]
sil = re.findall(r"silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)", run(["-af", "silencedetect=n=-40dB:d=2.5", "-vn"]))
out.append(f"① 소리 빈 틈 2.5초+ : {len(sil)} " + " ".join(f"{float(a):.1f}~{float(b):.1f}" for a, b in sil))
blk = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", run(["-vf", "blackdetect=d=0.5:pix_th=0.08", "-an"]))
out.append(f"② 까만 화면 0.5초+ : {len(blk)} " + " ".join(f"{float(a):.1f}~{float(b):.1f}" for a, b in blk))
fz = re.findall(r"freeze_start: ([\d.]+)[\s\S]*?freeze_end: ([\d.]+)", run(["-vf", "freezedetect=n=-72dB:d=1", "-an"]))
out.append(f"③ 멈춤 1초+ : {len(fz)} " + " ".join(f"{float(a):.1f}~{float(b):.1f}" for a, b in fz))
out.append(f"④ 끝 까만 화면: " + ("있음" if blk and float(blk[-1][1]) > dur - 1 and dur - float(blk[-1][0]) > 2 else "없음"))
open("finalcheck.txt", "w", encoding="utf-8").write("\n".join(out) + "\n"); print("\n".join(out))
T = list(range(5, int(dur), 20)); tiles = []
for t in T:
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", V, "-frames:v", "1", "-vf", "scale=320:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    open("_fc.png", "wb").write(b); im = Image.open("_fc.png").convert("RGB"); ImageDraw.Draw(im).text((4, 4), f"{t // 60}:{t % 60:02d}", fill=(255, 255, 0)); tiles.append(im)
w, h = tiles[0].size
for b0 in range(0, len(tiles), 30):
    S = tiles[b0:b0 + 30]; sh = Image.new("RGB", (w * 6, h * ((len(S) + 5) // 6)))
    for i, im in enumerate(S): sh.paste(im, ((i % 6) * w, (i // 6) * h))
    sh.save(f"finalcheck_{b0 // 30}.jpg", quality=85)
