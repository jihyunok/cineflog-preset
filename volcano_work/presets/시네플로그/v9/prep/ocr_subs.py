# -*- coding: utf-8 -*-
"""박힌 한국어 자막 OCR(윈도우 기본 OCR ko, 무료·로컬) → ../ko.srt · ../srt_ko.txt — 10-24 대작 08 언싱커블(자막 트랙 없이 그림 안에 한국어 자막).
작업 폴더 안 _ocr/ 에서 돌린다. 먼저 자막 띠를 2fps 로 뽑아 흑백 반전(검은 글자/흰 바탕):
  ffmpeg -i ../src.mp4 -an -vf "fps=2,crop=1320:200:300:840,format=gray,lut=y='if(gt(val\,200)\,0\,255)'" fr/%05d.png
그 뒤 python run_ocr.py (같은 폴더에 ocr_list.ps1). 밝은 장면은 글자가 깨지므로 같은 자막의 여러 프레임 중 한글 비율 높은 줄을 고른다.
결과 srt_ko.txt 를 토막 폴더에도 넣으면(_split_parts.py) 작업자가 대사 뜻을 공식 번역대로 쓴다(영어 받아쓰기만 있을 때보다 정확)."""
import os, subprocess, re, difflib
import numpy as np
from PIL import Image
fs = sorted(os.listdir("fr"))
keep = []
for f in fs:
    a = np.asarray(Image.open("fr/" + f))
    if (a < 128).sum() > 400: keep.append(f)
print("글자 있는 프레임", len(keep), "/", len(fs))
res = {}
CH = 400
for i in range(0, len(keep), CH):
    part = keep[i:i + CH]; lf = f"_list{i}.txt"; of = f"_out{i}.txt"
    if not os.path.exists(of):
        open(lf, "w", encoding="utf-8").write("\n".join(os.path.abspath("fr/" + f) for f in part))
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "ocr_list.ps1", os.path.abspath(lf), os.path.abspath(of)], check=True)
    for r in open(of, encoding="utf-8"):
        p = r.rstrip("\n").split("\t")
        if len(p) == 2 and p[1].strip(): res[p[0]] = p[1].strip()
    print(i + len(part), "/", len(keep), flush=True)
def hang(t): return re.sub(r"[^가-힣]", "", t)
def good(t):
    ok = len(re.findall(r"[가-힣0-9 ?!,.\-/]", t)); return ok / max(1, len(t)) + min(len(hang(t)), 30) / 300
ev = []
for f in fs:
    t = res.get(f, ""); s = (int(f[:5]) - 1) / 2
    if not t or len(hang(t)) < 2: continue
    if ev and s - ev[-1][1] <= 0.6 and difflib.SequenceMatcher(None, hang(ev[-1][3]), hang(t)).ratio() > 0.55:
        ev[-1][1] = s + 0.5; ev[-1][2].append(t)
        ev[-1][3] = max(ev[-1][2], key=good)
    else: ev.append([s, s + 0.5, [t], t])
ev = [(a, b, t) for a, b, _, t in ev]
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); sec = x % 60
    return f"{h:02d}:{m:02d}:{int(sec):02d},{int(round((sec - int(sec)) * 1000)):03d}"
open("../ko.srt", "w", encoding="utf-8").write("\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n" for i, (a, b, t) in enumerate(ev, 1)))
open("../srt_ko.txt", "w", encoding="utf-8").write("".join(f"{i}\t{a:.3f}\t{b:.3f}\t{t}\n" for i, (a, b, t) in enumerate(ev, 1)))
print("자막", len(ev))
