# -*- coding: utf-8 -*-
"""토막 X 의 나레 조각 시트(11-12 31v2): check.py X 를 돌린 뒤 _seg/wX/windows_dry.json 에서 토막 안(또는 고른 k) N 줄 조각마다
원본 프레임 두 장(조각 시작+0.1초 · 조각 가운데)을 뽑아 한 장에 6조각씩 시트로 → _seg/wX/pieces_NN.jpg. 칸 머리: k·조각 번호·화면초·원본초, 아래 띠에 나레 글(그 줄 전체).
조각은 문장 구간 앞에서부터 차례 — 글의 앞 토막이 앞 조각에 놓인다(글자 수 비례로 어림). 프레임은 원본(반전 전)이다.
사용: python D:/cine_work/ep31v2_잭리처/_seg/pieces.py X [k1 k2 …]"""
import json, os, subprocess, sys, tempfile, ast
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
X = sys.argv[1]; ONLY = {int(a) for a in sys.argv[2:]}
SEG = r"D:\cine_work\ep31v2_잭리처\_seg"; T = os.path.join(SEG, "w" + X); SRC = "D:/cine_work/ep31_잭리처/src.mp4"
ns = {}; exec(open(os.path.join(T, "script.py"), encoding="utf-8").read(), ns); S = ns["S"]
g = {}; exec(open(os.path.join(SEG, f"seg{X}.py"), encoding="utf-8").read(), g)
src = open(os.path.join(T, "script.py"), encoding="utf-8").read()
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
body = g["LINES"].strip("\n") + "\n"
# 토막 줄 범위: 시험 대본에서 LINES 가 들어간 자리(check.py 와 같은 계산)
osrc = open(r"D:\cine_work\ep31v2_잭리처\_v1_script.py", encoding="utf-8").read()
OSE = [n.value for n in ast.parse(osrc).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
a = OSE[g["SPAN"][0]].lineno - 1
kk = [k for k, e in enumerate(SE) if a + 1 <= e.lineno <= a + body.count("\n")]
K0, K1 = min(kk), max(kk)
W = json.load(open(os.path.join(T, "windows_dry.json"), encoding="utf-8"))
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
rows = []
for k in range(K0, K1 + 1):
    if S[k][0] != "N" or (ONLY and k not in ONLY): continue
    ws = [w for w in W if w.get("k") == k]
    tot = sum(w["b"] - w["a"] for w in ws) or 1; txt = S[k][1]; acc = 0
    for j, w in enumerate(ws):
        d = w["b"] - w["a"]; c0 = int(len(txt) * acc / tot); c1 = int(len(txt) * (acc + d) / tot); acc += d
        rows.append(dict(k=k, j=j, a=w["a"], s=w["s"], d=d, t1=w["s"] + 0.1, t2=w["s"] + d / 2, part=txt[c0:c1], txt=txt))
if not rows: print("조각 없음"); sys.exit()
tmp = tempfile.mkdtemp(); FW = 360
def grab(t):
    p = os.path.join(tmp, f"{t:.2f}.jpg")
    if not os.path.exists(p): subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", SRC, "-frames:v", "1", "-vf", f"scale={FW}:-2", p])
    return p
with ThreadPoolExecutor(3) as ex: list(ex.map(grab, [t for r in rows for t in (r["t1"], r["t2"])]))
try: F = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 17)
except Exception: F = ImageFont.load_default()
PER = 6; n = 0
for i in range(0, len(rows), PER):
    part = rows[i:i + PER]; im0 = Image.open(os.path.join(tmp, f"{part[0]['t1']:.2f}.jpg")); h = im0.height
    cell = h + 22 + 44; sheet = Image.new("RGB", (FW * 2 + 8, cell * len(part)), "black"); d = ImageDraw.Draw(sheet)
    for r_i, r in enumerate(part):
        y = r_i * cell
        d.text((4, y + 2), f"k{r['k']} 조각{r['j']} 화면 {mm(r['a'])} · 원본 {mm(r['s'])}~{mm(r['s'] + r['d'])}", fill="yellow", font=F)
        for c, t in enumerate((r["t1"], r["t2"])):
            p = os.path.join(tmp, f"{t:.2f}.jpg")
            if os.path.exists(p): sheet.paste(Image.open(p), (c * (FW + 8), y + 22))
        d.text((4, y + 22 + h + 2), f"~「{r['part']}」", fill="white", font=F)
        d.text((4, y + 22 + h + 22), r["txt"][:70], fill=(150, 150, 150), font=F)
    out = os.path.join(T, f"pieces_{n:02d}.jpg"); sheet.save(out, quality=85); print(out, len(part)); n += 1
