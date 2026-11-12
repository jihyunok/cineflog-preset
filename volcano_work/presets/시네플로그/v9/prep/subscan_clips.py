# -*- coding: utf-8 -*-
# ★사용법(11-03 ep38 에서 가져옴): 작업 폴더에 _subscan 또는 _txt 폴더를 만들어 이 파일을 넣고 그 폴더에서(subscan·textocr) / 작업 폴더에서(ocr_noflip) 돌린다. OCR 은 ../_ocr/ocr_list*.ps1(이 폴더의 ocr_list.ps1·ocr_list_en.ps1 을 _ocr 에 복사).
# 11-03 사용자 「중간에 원본 자막이 들어가 있어. 확인해」 — 잘린 조각(clips, 우리 자막 넣기 전)의 아래쪽에 박힌 한국어 자막이 남았는지 OCR(ko)로 전수 검사.
import os, re, subprocess, json
os.chdir(os.path.dirname(os.path.abspath(__file__)))
L = [l.split("'")[1] for l in open("../all.txt", encoding="utf-8") if "'" in l]
os.makedirs("fr", exist_ok=True)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip() or 0)
rows = []
t = 0.0
for i, c in enumerate(L):
    p = "../" + c; d = dur(p)
    for j, f in enumerate((0.1, 0.5, 0.9)):
        out = f"fr/{i:04d}_{j}.png"
        if not os.path.exists(out):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{d * f:.2f}", "-i", p, "-frames:v", "1", "-vf",
                            "crop=1320:300:300:780,format=gray,lut=y='if(gt(val\\,200)\\,0\\,255)'", out])
        rows.append((out, i, c, t + d * f))
    t += d
lf = os.path.abspath("_l.txt"); of = os.path.abspath("_o.txt")
open(lf, "w", encoding="utf-8").write("\n".join(os.path.abspath(r[0]) for r in rows if os.path.exists(r[0])))
subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.abspath("../_ocr/ocr_list.ps1"), lf, of], check=True)
res = {}
for r in open(of, encoding="utf-8"):
    p = r.rstrip("\n").split("\t")
    if len(p) == 2: res[p[0]] = p[1]
hits = []
for out, i, c, ts in rows:
    tx = res.get(os.path.basename(out), "")
    if len(re.findall(r"[가-힣]", tx)) >= 2: hits.append((i, c, round(ts, 1), tx))
seen = {}
for i, c, ts, tx in hits: seen.setdefault(i, (c, ts, tx))
for i, (c, ts, tx) in sorted(seen.items()): print(i, f"{int(ts//60)}:{ts%60:04.1f}", c, tx[:40])
json.dump([[i, c, ts, tx] for i, (c, ts, tx) in sorted(seen.items())], open("hits.json", "w", encoding="utf-8"), ensure_ascii=False)
print("걸린 조각", len(seen), "/", len(L))
