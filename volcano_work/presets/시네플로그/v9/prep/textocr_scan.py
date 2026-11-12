# -*- coding: utf-8 -*-
# ★사용법(11-03 ep38 에서 가져옴): 작업 폴더에 _subscan 또는 _txt 폴더를 만들어 이 파일을 넣고 그 폴더에서(subscan·textocr) / 작업 폴더에서(ocr_noflip) 돌린다. OCR 은 ../_ocr/ocr_list*.ps1(이 폴더의 ocr_list.ps1·ocr_list_en.ps1 을 _ocr 에 복사).
# 11-02 ep38: 반전 검수 앞당기기 — 원본 그림(자막 위, y138~800)을 1초마다 2배로 키워 윈도우 영어 OCR → 글자 있는 초 목록 text_sec.tsv
# 600장씩 뽑고 → OCR → 지움(디스크 아낌). 이어하기: 이미 한 묶음(_o{k}.txt)은 건너뜀.
import os, subprocess, sys
SRC, END, CH = "../src.mp4", 6018, 600
PS = os.path.abspath("../_ocr/ocr_list_en.ps1")
os.makedirs("fr", exist_ok=True)
for k in range(0, END, CH):
    of = f"_o{k}.txt"
    if os.path.exists(of): continue
    for f in os.listdir("fr"): os.remove("fr/" + f)
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(k), "-t", str(min(CH, END - k)), "-i", SRC, "-an",
                    "-vf", "fps=1,crop=1920:662:0:138,scale=3840:-1", "-q:v", "3", "-start_number", str(k), "fr/%05d.jpg"], check=True)
    fs = sorted(os.listdir("fr"))
    lf = os.path.abspath(f"_l{k}.txt"); open(lf, "w", encoding="utf-8").write("\n".join(os.path.abspath("fr/" + f) for f in fs))
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS, lf, os.path.abspath(of)], check=True)
    print(k, len(fs), flush=True)
rows = []
for k in range(0, END, CH):
    for r in open(f"_o{k}.txt", encoding="utf-8"):
        p = r.rstrip("\n").split("\t")
        if len(p) == 2 and sum(c.isalnum() for c in p[1]) >= 3: rows.append((int(p[0][:5]), p[1]))
open("text_sec.tsv", "w", encoding="utf-8").write("".join(f"{s}\t{t}\n" for s, t in rows))
print("글자 있는 초", len(rows))
