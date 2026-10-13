# -*- coding: utf-8 -*-
"""대사 컷(blocks/d*.mkv) 소리를 나레(-16 LUFS)와 같은 크기로 — 컷마다 재서 올리거나 내린다(+10 ~ -15dB), 리미터.
한국 영화 원본은 +17.5dB 로 키우면 나레보다 7~8dB 컸다(08~10편), 11편은 5dB 작았다. 사용: python dlevel.py <작업폴더>"""
import glob, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
T = -16.0
def lufs(p):
    o = subprocess.run(["ffmpeg", "-i", p, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", o); return float(m[-1]) if m else -70
def one(p):
    mk = p + ".lv"
    if os.path.exists(mk): return
    I = lufs(p); g = max(-15, min(10, T - I)) if I > -60 else 0
    if abs(g) >= 0.8:
        t = p[:-4] + "_t.mkv"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-c:v", "copy", "-af", f"volume={g:.1f}dB,alimiter=limit=0.95", "-c:a", "pcm_s16le", t], check=True)
        os.replace(t, p)
    open(mk, "w").write(f"{I} {g:.1f}")
ps = glob.glob(os.path.join(sys.argv[1], "blocks", "d*.mkv"))
with ThreadPoolExecutor(6) as ex: list(ex.map(one, ps))
gs = [float(open(p + ".lv").read().split()[1]) for p in ps]
print(sys.argv[1], len(ps), "컷 · 평균 조정", round(sum(gs) / len(gs), 1), "dB")
