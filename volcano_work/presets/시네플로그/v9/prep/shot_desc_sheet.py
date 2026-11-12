# -*- coding: utf-8 -*-
"""shot_desc.py 의 아끼기 판(10-28): 컷 그림 6장을 번호 붙인 한 장(2x3)으로 붙여 agy 에 보낸다 — agy 가 파일을 여는 횟수가 1/6 이라 사용량이 준다.
결과는 shot_desc.py 와 같은 shots.json(이미 설명 있는 컷·닮은 컷은 건너뜀). 그림 뽑기는 shot_desc.py 와 같은 임시 폴더를 다시 씀.
사용: python shot_desc_sheet.py [--workers 4] [--sheets 8] [--model claude-sonnet-5-5-low] [--only 시작초 끝초] [--test N]"""
import argparse, json, math, os, re, subprocess, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
CFG = json.load(open("ep.json", encoding="utf-8")); SRC = CFG["src"]; SRCLEN = CFG["srclen"]
ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--sheets", type=int, default=8)
ap.add_argument("--model", default="claude-sonnet-5-5-low"); ap.add_argument("--only", nargs=2, type=float)
ap.add_argument("--test", type=int, default=0, help="이미 설명 있는 컷 N개를 다시 받아 test_sheet.json 에 나란히(shots.json 안 바꿈)")
a = ap.parse_args()
shots = json.load(open("shots.json", encoding="utf-8"))
WORK = os.path.join(tempfile.gettempdir(), "agy_shots_" + re.sub(r"\W", "", os.path.basename(os.getcwd()), flags=re.A)); os.makedirs(WORK, exist_ok=True)
SW = os.path.join(WORK, "sheets"); os.makedirs(SW, exist_ok=True)
if a.test:
    import random; random.seed(7)
    todo = sorted(random.sample([x for x in shots if x.get("desc") and not x.get("same_as")], a.test), key=lambda x: x["i"])
else:
    todo = [x for x in shots if not x.get("desc")]
    if a.only: todo = [x for x in todo if a.only[0] <= x["s"] < a.only[1]]
    # 닮은 컷 이어받기(shot_desc.py 와 같은 판정)
    import numpy as np
    if os.path.exists("fp_src.npy"):
        FP = np.load("fp_src.npy", mmap_mode="r")
        def vec(x):
            v = np.concatenate([np.asarray(FP[min(len(FP) - 1, int((x["s"] + (x["e"] - x["s"]) * f) * 4))]).ravel() for f in (0.3, 0.5, 0.7)]).astype(np.float32)
            v -= v.mean(); n = np.linalg.norm(v); return v / n if n > 1e-6 else v
        reps = []; SAME = {}
        for x in shots:
            v = vec(x); best = max(((float(v @ rv), r) for r, rv in reps[-8:]), default=(-1, None))
            if best[0] >= 0.8: SAME[x["i"]] = best[1]
            else: reps.append((x["i"], v))
        todo = [x for x in todo if x["i"] not in SAME]
    else: SAME = {}
print("남은 컷", len(todo), flush=True)
def frame(x):
    p = os.path.join(WORK, f"s{x['i']:04d}.jpg")
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(x['s'] + x['e']) / 2:.2f}", "-i", SRC, "-frames:v", "1", "-vf", "scale=560:-2", "-q:v", "4", p], check=True)
    return p
with ThreadPoolExecutor(8) as ex: list(ex.map(frame, todo))
groups = [todo[i:i + 6] for i in range(0, len(todo), 6)]
FONT = r"C\:/Windows/Fonts/arialbd.ttf"
def sheet(g):
    p = os.path.join(SW, f"t{g[0]['i']:05d}.jpg")
    if os.path.exists(p): return p
    ins = []; fl = []
    for k, x in enumerate(g):
        ins += ["-i", os.path.join(WORK, f"s{x['i']:04d}.jpg")]
        fl.append(f"[{k}:v]scale=560:315,drawbox=x=0:y=0:w=70:h=46:color=black@0.8:t=fill,drawtext=fontfile='{FONT}':text='{k + 1}':x=18:y=6:fontsize=36:fontcolor=yellow[v{k}]")
    for k in range(len(g), 6): ins += ["-f", "lavfi", "-i", "color=black:s=560x315:d=1"]; fl.append(f"[{k}:v]null[v{k}]")
    fl.append("".join(f"[v{k}]" for k in range(6)) + "xstack=inputs=6:layout=0_0|w0_0|0_h0|w0_h0|0_h0+h1|w0_h0+h1:fill=white[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[o]", "-frames:v", "1", "-q:v", "4", p], check=True)
    return p
with ThreadPoolExecutor(6) as ex: paths = list(ex.map(sheet, groups))
SCH = os.path.join(SW, "schema.json")
json.dump({"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "sheet": {"type": "string"}, "n": {"type": "integer"}, "desc": {"type": "string"}}, "required": ["sheet", "n", "desc"]}}}, "required": ["items"]}, open(SCH, "w"))
lock = threading.Lock(); TEST = {}
def save(): json.dump(shots, open("shots.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
PL = " / ".join(CFG.get("places", []) + ["other"]); WHO = " / ".join(CFG.get("who", []) + ["nobody"])
def run(bi):
    bg = groups[bi:bi + a.sheets]; names = [os.path.basename(paths[groups.index(g)]) for g in bg]
    prompt = (f"명령어(터미널)는 쓰지 말고, 이 폴더의 아래 그림 파일들을 하나씩 직접 열어 봐. {CFG.get('ctx', '')} 의 장면들이다. "
              "그림 한 장에 서로 다른 장면 6칸(2열 3줄, 왼쪽 위 노란 번호 1~6 — 1 2 / 3 4 / 5 6 순서)이 붙어 있다. 칸끼리는 상관없는 다른 컷이다. 검은 빈 칸은 빼.\n"
              + "\n".join(names) +
              f"\n\n칸마다 desc 는 **영어** 한 문장(25단어 안)으로: place ({PL}) · who is visible ({WHO}) · what they are doing or what happens (fight, gunshot, explosion, car chase, hugging, talking, eating …) · day/night."
              " 본 것만 적어(짐작 금지). sheet 칸에는 파일 이름 그대로, n 은 칸 번호.")
    for t in range(3):
        try:
            r = subprocess.run([AGY, "--model", a.model, "-p", prompt, "--print-timeout", "500s", "--output-format", "json", "--disable-slash-commands", "--json-schema", SCH],
                               cwd=SW, capture_output=True, timeout=560)
            out = r.stdout.decode("utf-8", "replace"); j = json.loads(out[out.find("{"):])
            resp = j.get("response") or ""; body = json.loads(resp[resp.find("{"):resp.rfind("}") + 1])
            got = {(it["sheet"].strip(), int(it["n"])): it["desc"].strip() for it in body.get("items", [])}
            n = 0; tot = sum(len(g) for g in bg)
            with lock:
                for g, nm in zip(bg, names):
                    for k, x in enumerate(g):
                        d = got.get((nm, k + 1))
                        if d:
                            n += 1
                            if a.test: TEST[x["i"]] = d
                            else: x["desc"] = d
                if not a.test: save()
            print(f"  {names[0]}~ {n}/{tot}", flush=True)
            if n >= tot * 0.8: return
        except Exception as e:
            print(f"  {names[0]}~ 실패 {str(e)[:120]}", flush=True); time.sleep(30)
with ThreadPoolExecutor(a.workers) as ex: list(ex.map(run, range(0, len(groups), a.sheets)))
if a.test:
    json.dump([{"i": x["i"], "old": x["desc"], "sheet": TEST.get(x["i"], "")} for x in todo], open("test_sheet.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("시험", len(TEST), "/", len(todo))
else:
    for i, r in SAME.items():
        if not shots[i].get("desc") and shots[r].get("desc"): shots[i]["desc"] = shots[r]["desc"]; shots[i]["same_as"] = r
    save(); print("끝 · 설명 있는 컷", sum(1 for x in shots if x.get("desc")), "/", len(shots))
