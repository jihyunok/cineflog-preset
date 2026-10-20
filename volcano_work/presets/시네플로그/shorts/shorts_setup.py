# -*- coding: utf-8 -*-
"""영화 리뷰 쇼츠 작업 폴더 준비(다른 PC 「대작」에서 10-20 가져옴) — 롱폼 작업 폴더 안 쇼츠 폴더(예: ep03_…/shorts01)에서 돌린다.
10-20 사용자 "아니야. 이템플릿으로 할거야. 그건 다른채널이야" → 쇼츠는 이 템플릿(극장 위·아래 띠)으로, 짜기·자르기는 v9 그대로(plan_v9 · build_v9 cut · gate).
- 쇼츠 script.py 의 나레 줄(N)마다 롱폼 narr/nNNN.json 에서 글이 똑같은 줄을 찾아 1.35배(atempo, 음높이 그대로)로 narr/ 에 복사한다
  (README 「쇼츠 나레는 롱폼 녹음 조각을 잘라 1.35배로 쓰고, 롱폼에 없는 줄만 한 묶음으로 새로 녹음」 — TTS 호출 0).
  롱폼에 없는 줄은 「새로 녹음할 줄」로 찍는다(mkbatch.py → AI 스튜디오 한 묶음 → gem_split.py --speed 1.35).
- ep.json 은 롱폼 것을 절대 경로로 바꿔 쓰고 쇼츠 값(min_total 90 · narr_speed 1.35)만 덮는다. lines.json·black_src.npy·shots.json 복사, narr_en.json 은 같은 글 줄만.
사용: python shorts_setup.py [--speed 1.35]"""
import glob, json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
SPEED = float(sys.argv[sys.argv.index("--speed") + 1]) if "--speed" in sys.argv else 1.35
LF = os.path.dirname(os.getcwd())                     # 롱폼 작업 폴더
ab = lambda p: p if os.path.isabs(p) or p.startswith("~") else os.path.join(LF, p).replace("\\", "/")
cfg = json.load(open(f"{LF}/ep.json", encoding="utf-8"))
for k in ("scenes", "words", "band", "bench", "fonts", "emph"):
    if k in cfg: cfg[k] = ab(cfg[k])
cfg.update(min_total=90, min_total_why="쇼츠 — 길이는 명화관처럼 1:40~2:30(10-19 \"길이는 명화관처럼\")", narr_speed=SPEED, clips="clips",
           shorts=True)   # 관문 ⑭⑮(롱폼 앞 3분 규칙)는 쇼츠에서 안 잰다
for k in ("capstyle", "capstyle_why"): cfg.pop(k, None)
json.dump(cfg, open("ep.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for f in ("lines.json", "black_src.npy", "shots.json"):
    if os.path.exists(f"{LF}/{f}"): shutil.copy2(f"{LF}/{f}", f)
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
# ★10-20 03 v2 쇼츠: 글자 컷(비 오는 월마트 간판·인터뷰 마이크)이 거꾸로 나옴 — 쇼츠 대본엔 롱폼의 noflip 이 없었다 → 롱폼 script.py 에서 같은 줄(N 글·D 줄 id·A 구간)의 noflip 을 옮겨 script.py 를 다시 쓴다
cwd = os.getcwd(); os.chdir(LF); nsl = {}; exec(open("script.py", encoding="utf-8").read(), nsl); os.chdir(cwd)
def _nf(x): return isinstance(x[-1], dict) and x[-1].get("noflip")
def _key(x):
    if x[0] == "D": return ("D", tuple(x[1] if isinstance(x[1], list) else [x[1]]))
    if x[0] == "A": return ("A", x[1], x[2])
    return ("N", x[1]) if x[0] == "N" else None
NF = {_key(x) for x in nsl["S"] if _nf(x)}; add = 0; S2 = []
for x in ns["S"]:
    if _key(x) in NF and not _nf(x):
        op = dict(x[-1]) if isinstance(x[-1], dict) else {}; x = tuple(x[:-1] if isinstance(x[-1], dict) else x) + (dict(op, noflip=True),); add += 1
    S2.append(x)
if add:
    src = open("script.py", encoding="utf-8").read()
    open("script.py", "w", encoding="utf-8").write(src.split("S = [")[0] + "S = [\n" + "".join(repr(x) + ",\n" for x in S2) + "]\n"); ns["S"] = S2
    print("롱폼 noflip 옮김", add, "줄")
lf = {}
for p in sorted(glob.glob(f"{LF}/narr/n*.json")):
    lf.setdefault(json.load(open(p, encoding="utf-8"))["text"], p)
en_l = json.load(open(f"{LF}/narr_en.json", encoding="utf-8")) if os.path.exists(f"{LF}/narr_en.json") else {}
os.makedirs("narr", exist_ok=True); en = {}; ni = 0; new = []
for x in ns["S"]:
    if x[0] != "N": continue
    ni += 1; src = lf.get(x[1]); out = f"narr/n{ni:03d}"
    if not src: new.append((ni, x[1])); continue
    j = json.load(open(src, encoding="utf-8")); lni = os.path.basename(src)[1:4]
    if str(int(lni)) in en_l: en[str(ni)] = en_l[str(int(lni))]
    if os.path.exists(out + ".json") and json.load(open(out + ".json", encoding="utf-8")).get("from") == [src, SPEED]: continue
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src[:-5] + ".wav", "-af", f"atempo={SPEED:.4f},aresample=48000", "-ac", "2", "-c:a", "pcm_s16le", out + ".wav"], check=True)
    j["st"] = [round(t / SPEED, 3) for t in j["st"]]; j["en"] = [round(t / SPEED, 3) for t in j["en"]]
    j["from"] = [src, SPEED]
    json.dump(j, open(out + ".json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(en, open("narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", ni, "줄 · 롱폼 녹음 다시 씀", ni - len(new), f"({SPEED}배) · 새로 녹음할 줄", len(new))
for n, t in new: print(f"  n{n:03d} {t}")
