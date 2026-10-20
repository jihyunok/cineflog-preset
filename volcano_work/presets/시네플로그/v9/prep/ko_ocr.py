# -*- coding: utf-8 -*-
"""원본에 박힌 한국어 자막 → srt.txt (번호\t시작\t끝\t글) — 05v2 토탈리 킬러(10-18).
① 자막 띠(crop 1200x144 @ 360,790)를 5fps 로 훑어 흰 글자+어두운 테두리 마스크 → 켜짐/꺼짐·모양 바뀜으로 자막 한 장씩(옛 05 tools/subdet·events 와 같은 잣대)
② 장마다 가운데 프레임의 자막 띠를 잘라 PNG → agy(제미나이, 구독)에게 40장씩 읽힘(shot_desc 와 같은 방식, 명령어 금지)
★자막 띠 자리(crop 1200x144@360,790 · 잘라낼 띠 1400x160@260,780)는 1920x960 원본 기준 — 다른 원본이면 프레임을 보고 고친다.
사용: python ko_ocr.py [--workers 3]  (작업 폴더에서. 결과 subev.json·ko_ocr.json·srt.txt — 이름 표기는 나레와 맞춰 바꿀 것)"""
import argparse, json, os, re, subprocess, tempfile, threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
CFG = json.load(open("ep.json", encoding="utf-8")); SRC = CFG["src"]
ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); ap.add_argument("--batch", type=int, default=40)
A = ap.parse_args()
W, H, FPS = 600, 72, 5
if not os.path.exists("subev.json"):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-threads", "8", "-i", SRC, "-vf", f"fps={FPS},crop=1200:144:360:790,scale={W}:{H},format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    B = []
    while True:
        b = p.stdout.read(W * H)
        if len(b) < W * H: break
        a = np.frombuffer(b, np.uint8).reshape(H, W).astype(np.int16)
        br = a > 215; dk = np.zeros_like(br)
        dk[:, 2:] |= a[:, :-2] < 100; dk[:, :-2] |= a[:, 2:] < 100
        B.append(br & dk)
    B = np.array(B); on = B.sum((1, 2)) > 60
    def iou(x, y):
        u = (x | y).sum(); return (x & y).sum() / u if u else 1
    ev = []; cur = None
    for k in range(len(B)):
        if not on[k]:
            if cur: ev.append(cur); cur = None
            continue
        if cur and iou(B[k], B[cur["ref"]]) > 0.45: cur["e"] = k; continue
        if cur: ev.append(cur)
        cur = {"s": k, "e": k, "ref": k}
    if cur: ev.append(cur)
    out = [{"s": round(e["s"] / FPS, 2), "e": round((e["e"] + 1) / FPS, 2)} for e in ev if e["e"] - e["s"] >= 2]
    for i, e in enumerate(out): e["id"] = i + 1
    json.dump(out, open("subev.json", "w"), indent=0)
    print("자막 장", len(out), flush=True)
EV = json.load(open("subev.json"))
WORK = os.path.join(tempfile.gettempdir(), "agy_kosub_" + re.sub(r"\W", "", os.path.basename(os.getcwd()), flags=re.A)); os.makedirs(WORK, exist_ok=True)
def strip(e):
    p = os.path.join(WORK, f"k{e['id']:04d}.png")
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(e['s'] + e['e']) / 2:.2f}", "-i", SRC, "-frames:v", "1", "-vf", "crop=1400:160:260:780", p], check=True)
    return p
with ThreadPoolExecutor(8) as ex: list(ex.map(strip, EV))
OUT = "ko_ocr.json"
got = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
SCH = os.path.join(WORK, "schema.json")
json.dump({"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "file": {"type": "string"}, "text": {"type": "string"}}, "required": ["file", "text"]}}}, "required": ["items"]}, open(SCH, "w", encoding="utf-8"))
lock = threading.Lock()
def run(batch):
    names = [f"k{e['id']:04d}.png" for e in batch]
    prompt = ("명령어(터미널)는 쓰지 말고, 이 폴더의 아래 그림 파일들을 하나씩 직접 열어 봐. 영화 자막 띠를 잘라 낸 그림이다.\n" + "\n".join(names) +
              "\n\n그림마다 흰 글씨 한국어 자막을 **보이는 그대로** 받아 적어(고치거나 번역하지 말 것). 두 줄이면 줄 사이에 ' / ' 를 넣어. 줄 앞 '-' 는 그대로 둬."
              " 자막이 없거나 못 읽으면 text 를 빈 문자열로. file 칸에는 파일 이름 그대로.")
    for k in range(3):
        try:
            r = subprocess.run([AGY, "-p", prompt, "--print-timeout", "400s", "--output-format", "json", "--disable-slash-commands", "--json-schema", SCH],
                               cwd=WORK, capture_output=True, timeout=460)
            o = r.stdout.decode("utf-8", "replace"); j = json.loads(o[o.find("{"):])
            resp = j.get("response") or ""; body = json.loads(resp[resp.find("{"):resp.rfind("}") + 1])
            g = {it["file"].strip(): it["text"].strip() for it in body.get("items", [])}
            n = 0
            with lock:
                for e, nm in zip(batch, names):
                    if nm in g: got[str(e["id"])] = g[nm]; n += 1
                json.dump(got, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
            print(f"  {names[0]}~ {n}/{len(batch)}", flush=True)
            if n >= len(batch) * 0.8: return
        except Exception as ex:
            print("  다시", names[0], ex, flush=True)
todo = [e for e in EV if str(e["id"]) not in got]
print("남은", len(todo), flush=True)
bs = [todo[i:i + A.batch] for i in range(0, len(todo), A.batch)]
with ThreadPoolExecutor(A.workers) as ex: list(ex.map(run, bs))
with open("srt.txt", "w", encoding="utf-8") as f:
    n = 0
    for e in EV:
        t = (got.get(str(e["id"])) or "").strip()
        if t: f.write(f"{e['id']}\t{e['s']:.2f}\t{e['e']:.2f}\t{t}\n"); n += 1
print("srt.txt", n, "줄", flush=True)
