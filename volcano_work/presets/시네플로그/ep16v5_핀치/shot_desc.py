# -*- coding: utf-8 -*-
"""원본 영화 컷마다 그림 한 장을 agy(제미나이, 구독)에게 보여 주고 「장소 · 인물 · 하는 일」 영어 한 문장을 받는다 (10-13, 제브는 영어가 가장 정확 — docs state.md).
사용자 "3분쯤에 핀치가 대피하고 씻는 장면이 중간중간 나와" / "제브사용해" — 제브는 글만 읽으므로, 그림 → 글은 agy, 같은 장면인지 판정은 제브.
컷 = ../ep16v4_핀치/scenes.txt 의 장면 전환. 결과 shots.json [{i, s, e, desc}]. 이미 받은 컷은 건너뜀(이어하기).
사용: python shot_desc.py [--workers 6] [--batch 40]"""
import argparse, json, os, re, subprocess, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
SRC = "../ep16v4_핀치/src.mp4"; SRCLEN = 6939.6
ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=6); ap.add_argument("--batch", type=int, default=40)
a = ap.parse_args()
cuts = sorted(float(x) for x in re.findall(r"pts_time:([\d.]+)", open("../ep16v4_핀치/scenes.txt").read()))
edges = [0.0] + cuts + [SRCLEN]
shots = [{"i": i, "s": round(s, 2), "e": round(e, 2)} for i, (s, e) in enumerate(zip(edges, edges[1:]))]
OUT = "shots.json"
old = {x["i"]: x for x in json.load(open(OUT, encoding="utf-8"))} if os.path.exists(OUT) else {}
for x in shots:
    if x["i"] in old and old[x["i"]].get("desc"): x["desc"] = old[x["i"]]["desc"]
WORK = os.path.join(tempfile.gettempdir(), "agy_shots"); os.makedirs(WORK, exist_ok=True)
todo = [x for x in shots if not x.get("desc")]
print("컷", len(shots), "· 남은", len(todo), flush=True)
def frame(x):
    p = os.path.join(WORK, f"s{x['i']:04d}.jpg")
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(x['s'] + x['e']) / 2:.2f}", "-i", SRC, "-frames:v", "1", "-vf", "scale=480:-2", "-q:v", "4", p], check=True)
    return p
with ThreadPoolExecutor(8) as ex: list(ex.map(frame, todo))
SCH = os.path.join(WORK, "schema.json")
json.dump({"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "file": {"type": "string"}, "desc": {"type": "string"}}, "required": ["file", "desc"]}}}, "required": ["items"]},
    open(SCH, "w", encoding="utf-8"), ensure_ascii=False)
lock = threading.Lock(); stop = [False]
def save():
    json.dump(shots, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
def run(batch):
    if stop[0]: return
    names = [f"s{x['i']:04d}.jpg" for x in batch]
    prompt = ("명령어(터미널)는 쓰지 말고, 이 폴더의 아래 그림 파일들을 하나씩 직접 열어 봐. 영화 「Finch」(Tom Hanks as Finch, a humanoid robot later named Jeff, a small wheeled robot Dewey, a dog, post-apocalyptic desert)의 장면들이다.\n"
              + "\n".join(names) +
              "\n\n그림마다 desc 는 **영어** 한 문장(25단어 안)으로: place (indoor/outdoor, where) · who is visible (Finch / humanoid robot / Dewey / dog / other) · what they are doing · weather or day/night."
              " 본 것만 적어(짐작 금지). 못 열었으면 desc 에 'CANNOT OPEN'. file 칸에는 파일 이름 그대로.")
    for k in range(2):
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
