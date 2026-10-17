# -*- coding: utf-8 -*-
"""원본 영화 컷마다 그림 한 장을 agy(제미나이, 구독)에게 보여 주고 「장소 · 인물 · 하는 일」 영어 한 문장을 받는다 (10-13, 제브는 영어가 가장 정확).
컷 = scenes.txt 장면 전환, 4.5초 넘는 컷은 4.5초 안짝 토막. 결과 shots.json [{i, cut, s, e, desc}]. 이미 받은 컷은 건너뜀(이어하기).
작업 폴더 ep.json: src · srclen · ctx(영화 소개 영어 — 제목·연도·배우 역·줄거리 배경) · places(장소 낱말 목록) · who(인물 이름 목록)
사용: python shot_desc.py [--workers 6] [--batch 40]"""
import argparse, json, math, os, re, subprocess, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
CFG = json.load(open("ep.json", encoding="utf-8")); SRC = CFG["src"]; SRCLEN = CFG["srclen"]
ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=6); ap.add_argument("--batch", type=int, default=40)
a = ap.parse_args()
cuts = sorted(float(x) for x in re.findall(r"(\d+\.\d+)", open(CFG.get("scenes", "scenes.txt")).read()))
edges = [0.0] + cuts + [SRCLEN]
shots = []
for k, (s0, e0) in enumerate(zip(edges, edges[1:])):
    n = max(1, math.ceil((e0 - s0) / 4.5))
    for j in range(n): shots.append({"i": len(shots), "cut": k, "s": round(s0 + (e0 - s0) * j / n, 2), "e": round(s0 + (e0 - s0) * (j + 1) / n, 2)})
OUT = "shots.json"
old = {x["i"]: x for x in json.load(open(OUT, encoding="utf-8"))} if os.path.exists(OUT) else {}
for x in shots:
    o = old.get(x["i"])
    if o and o.get("desc") and abs(o["s"] - x["s"]) < 0.01: x["desc"] = o["desc"]
WORK = os.path.join(tempfile.gettempdir(), "agy_shots_" + re.sub(r"\W", "", os.path.basename(os.getcwd()), flags=re.A)); os.makedirs(WORK, exist_ok=True)
todo = [x for x in shots if not x.get("desc")]
print("컷", len(shots), "· 남은", len(todo), flush=True)
def frame(x):
    p = os.path.join(WORK, f"s{x['i']:04d}.jpg")
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(x['s'] + x['e']) / 2:.2f}", "-i", SRC, "-frames:v", "1", "-vf", "scale=560:-2", "-q:v", "4", p], check=True)
    return p
with ThreadPoolExecutor(8) as ex: list(ex.map(frame, todo))
SCH = os.path.join(WORK, "schema.json")
json.dump({"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "file": {"type": "string"}, "desc": {"type": "string"}}, "required": ["file", "desc"]}}}, "required": ["items"]},
    open(SCH, "w", encoding="utf-8"), ensure_ascii=False)
lock = threading.Lock(); stop = [False]
def save(): json.dump(shots, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
PL = " / ".join(CFG.get("places", []) + ["other"]); WHO = " / ".join(CFG.get("who", []) + ["nobody"])
def run(batch):
    if stop[0]: return
    names = [f"s{x['i']:04d}.jpg" for x in batch]
    prompt = (f"명령어(터미널)는 쓰지 말고, 이 폴더의 아래 그림 파일들을 하나씩 직접 열어 봐. {CFG.get('ctx', '')} 의 장면들이다. 그림 아래 한국어 자막이 있으면 무시해.\n"
              + "\n".join(names) +
              f"\n\n그림마다 desc 는 **영어** 한 문장(25단어 안)으로: place ({PL}) · who is visible ({WHO}) · what they are doing or what happens (fight, gunshot, explosion, car chase, hugging, talking, eating …) · day/night."
              " 본 것만 적어(짐작 금지). 못 열었으면 desc 에 'CANNOT OPEN'. file 칸에는 파일 이름 그대로.")
    for k in range(3):
        try:
            r = subprocess.run([AGY, "-p", prompt, "--print-timeout", "400s", "--output-format", "json", "--disable-slash-commands", "--json-schema", SCH],
                               cwd=WORK, capture_output=True, timeout=460)
            out = r.stdout.decode("utf-8", "replace"); j = json.loads(out[out.find("{"):])
            resp = j.get("response") or ""; body = json.loads(resp[resp.find("{"):resp.rfind("}") + 1])
            got = {it["file"].strip(): it["desc"].strip() for it in body.get("items", [])}
            n = 0
            with lock:
                for x, nm in zip(batch, names):
                    d = got.get(nm)
                    if d and "CANNOT OPEN" not in d: x["desc"] = d; n += 1
                save()
            print(f"  {names[0]}~ {n}/{len(batch)}", flush=True)
            if n >= len(batch) * 0.8: return
        except Exception as e:
            print(f"  {names[0]}~ 실패 {str(e)[:120]}", flush=True)
            time.sleep(20)
batches = [todo[i:i + a.batch] for i in range(0, len(todo), a.batch)]
with ThreadPoolExecutor(a.workers) as ex: list(ex.map(run, batches))
save()
print("끝 · 설명 있는 컷", sum(1 for x in shots if x.get("desc")), "/", len(shots))
