# -*- coding: utf-8 -*-
"""★11-07 글자 조각 자동 찾기 — 좌우반전하면 글자가 거꾸로 보이는 조각(택시 지붕 TAXI·간판·신문·번호판·화면 글자)을 agy(제미나이, 구독)로 찾는다.
(33 콜래트럴: 택시 지붕 「IXAT」 등 글자 컷 7곳 반전 — 업로드 메모 「글자 컷 빼고 반전」과 다름)
windows.json 의 모든 조각(반전 여부 상관없이) 원본 s+0.2 · 가운데 · 끝−0.2 프레임(원본 0.6초 안 조각은 가운데 하나)을 0.1초 단위로 _tf/ 에 뽑아(480 폭, 반전 안 함)
agy 에 40장씩 묻는다(4명 동시, 3번까지 · 20초 쉼). 답은 _tf/results.json 에 쌓여 plan 을 다시 짜도 새 프레임만 묻는다. API 키 안 씀 — agy 만.
결과 text_scan.json: scanned(답을 다 받은 조각의 원본 구간, 합침) · text(글자 보인 조각 원본 구간 + manual) · manual(사람이 더한 것, 그대로 둠)
→ plan_v9 가 text 구간과 겹치는 조각을 noflip · gate ⑰ 이 검사 안 된 반전 조각·글자 겹친 반전 조각을 막는다.
사용: python textflip.py [--workers 4] [--batch 40] [--limit N(앞 N 조각만 보냄, 시험)]
      python textflip.py --add S E "글자"   (사람이 본 글자 구간 원본 S~E초 더하기)"""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
OUT, TF = "text_scan.json", "_tf"; RES = os.path.join(TF, "results_v2.json")   # ★11-07 v2 물음(눈에 띄는 글자만 — 33 택시 영화에서 「작은 글자도」는 조각 55%가 걸림)
ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--batch", type=int, default=40)
ap.add_argument("--limit", type=int, default=0); ap.add_argument("--add", nargs=3, metavar=("S", "E", "WHAT"))
A = ap.parse_args()
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
def rows(L): return [(float(r[0]), float(r[1]), str(r[2]) if len(r) > 2 else "") for r in L]
def merge(rs):
    out = []
    for a, b, t in sorted(rs):
        if out and a <= out[-1][1] + 0.01:
            out[-1][1] = max(out[-1][1], b)
            if t and t not in out[-1][2].split(" / "): out[-1][2] = (out[-1][2] + " / " + t if out[-1][2] else t)[:120]
        else: out.append([a, b, t])
    return [[round(a, 2), round(b, 2), t] for a, b, t in out]
def save_out(T):
    json.dump(T, open(OUT + ".tmp", "w", encoding="utf-8"), ensure_ascii=False, indent=1); os.replace(OUT + ".tmp", OUT)
OLD = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
MAN = OLD.get("manual", [])
if A.add:
    s, e, what = float(A.add[0]), float(A.add[1]), A.add[2]
    if e <= s: sys.exit("E 가 S 보다 커야 한다")
    MAN.append([round(s, 2), round(e, 2), what]); OLD["manual"] = MAN; OLD.setdefault("scanned", [])
    OLD["text"] = merge(rows(OLD.get("text", [])) + [(s, e, what)]); save_out(OLD)
    print(f"manual 더함: 원본 {mm(s)}~{mm(e)} 「{what}」 · manual {len(MAN)}건 — plan_v9 다시 짜면 그 구간 조각 noflip"); sys.exit()

CFG = json.load(open("ep.json", encoding="utf-8")); SRC = CFG["src"]
W = json.load(open("windows.json", encoding="utf-8"))
def rate(w): return w.get("rate", 1.05 if w["kind"] == "A" else 1.0)
def s0(w): return w["s"] - w.get("pre", 0)
def slen(w): return (w["b"] - w["a"]) * rate(w)
def key(t): return f"{max(t, 0):.1f}"
def fname(k): return f"t{int(round(float(k) * 10)):06d}.jpg"
def keys(w):
    s, L = s0(w), slen(w)
    return list(dict.fromkeys(key(t) for t in ([s + L / 2] if L < 0.6 else [s + 0.2, s + L / 2, s + L - 0.2])))
WK = [keys(w) for w in W]
SEND = range(min(A.limit, len(W))) if A.limit else range(len(W))
os.makedirs(TF, exist_ok=True)
R = json.load(open(RES, encoding="utf-8")) if os.path.exists(RES) else {}
need = sorted({k for i in SEND for k in WK[i] if k not in R}, key=float)
print(f"조각 {len(W)}" + (f" (앞 {len(SEND)}개만 보냄 --limit)" if A.limit else "") + f" · 이미 답 받은 프레임 {len(R)} · 새로 물을 프레임 {len(need)}", flush=True)
def grab(k):
    p = os.path.join(TF, fname(k))
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", k, "-i", SRC, "-frames:v", "1", "-vf", "scale=480:-2", "-q:v", "4", p + ".tmp.jpg"])
        if os.path.exists(p + ".tmp.jpg"): os.replace(p + ".tmp.jpg", p)
    return os.path.exists(p)
with ThreadPoolExecutor(8) as ex: okf = list(ex.map(grab, need))
nofr = [k for k, o in zip(need, okf) if not o]
todo = [k for k, o in zip(need, okf) if o]
if nofr: print(f"  프레임 못 뽑음 {len(nofr)} (원본 {', '.join(nofr[:5])}초 …)", flush=True)
# agy 는 shot_desc.py 처럼 ASCII 임시 폴더에서 돌린다(작업 폴더 한글 경로 피함) — _tf/ 의 그림을 복사해 넣음
WORK = os.path.join(tempfile.gettempdir(), "agy_tf_" + re.sub(r"\W", "", os.path.basename(os.getcwd()), flags=re.A) + hashlib.md5(os.getcwd().encode("utf-8")).hexdigest()[:6])
os.makedirs(WORK, exist_ok=True)
SCH = os.path.join(WORK, "schema.json")
json.dump({"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "file": {"type": "string"}, "text": {"type": "boolean"}, "what": {"type": "string"}}, "required": ["file", "text", "what"]}}}, "required": ["items"]},
    open(SCH, "w", encoding="utf-8"), ensure_ascii=False)
lock = threading.Lock()
def save_res():
    json.dump(R, open(RES + ".tmp", "w", encoding="utf-8"), ensure_ascii=False, indent=0); os.replace(RES + ".tmp", RES)
def tbool(v): return v is True or (isinstance(v, str) and v.strip().lower() in ("true", "yes", "1"))
def run(batch):
    left = list(batch)
    for k in range(3):
        names = [fname(x) for x in left]
        for nm in names:
            if not os.path.exists(os.path.join(WORK, nm)): shutil.copy(os.path.join(TF, nm), os.path.join(WORK, nm))
        prompt = ("명령어(터미널)는 쓰지 말고, 이 폴더의 아래 그림 파일들을 하나씩 직접 열어 봐. 영화 장면이다.\n" + "\n".join(names) +
                  "\n\n그림마다: 좌우반전하면 거꾸로 된 글자가 **눈에 띌** 만큼 또렷한 글자·낱말·로고가 보이면 text=true — 간판·가게 이름, 신문 제목, 택시 지붕 표시(TAXI 등), "
                  "차 안 인쇄 안내문, 화면·모니터의 낱말, 포스터·광고, 상표·라벨, 가까이 잡힌 번호판, 크레디트 글자. 일부만 보여도 읽히면 true. "
                  "글자가 아주 작거나 흐려서 읽을 수 없으면, 또는 계기판·시계 숫자처럼 뒤집어도 티가 안 나는 것뿐이면 false. 화면 아래 한국어 자막은 무시(따로 다룬다). "
                  "what 에는 보인 글자를 짧게(예: 'TAXI 지붕 표시', '안내문 DRIVER CARRIES ONLY', '간판 HOTEL'), false 면 빈 칸. "
                  "못 열었으면 what 에 'CANNOT OPEN'. file 칸에는 파일 이름 그대로.")
        try:
            r = subprocess.run([AGY, "--model", os.environ.get("AGY_MODEL", "gemini-3.8-flash-high"), "-p", prompt, "--print-timeout", "400s", "--output-format", "json",
                                "--disable-slash-commands", "--json-schema", SCH], cwd=WORK, capture_output=True, timeout=460)
            out = r.stdout.decode("utf-8", "replace"); j = json.loads(out[out.find("{"):])
            resp = j.get("response") or ""; body = json.loads(resp[resp.find("{"):resp.rfind("}") + 1])
            got = {os.path.basename(str(it.get("file", "")).strip()): (tbool(it.get("text")), str(it.get("what") or "").strip()) for it in body.get("items", [])}
            with lock:
                for x, nm in zip(left, names):
                    g = got.get(nm)
                    if g is not None and "CANNOT OPEN" not in g[1].upper(): R[x] = {"text": g[0], "what": g[1] if g[0] else ""}
                save_res()
            n = sum(1 for x in left if x in R); left = [x for x in left if x not in R]
            print(f"  {names[0]}~ {n}/{len(names)}" + (f" · 남은 {len(left)}" if left else ""), flush=True)
        except Exception as e:
            print(f"  {names[0]}~ 실패({k + 1}/3) {str(e)[:120]}", flush=True)
        if not left: return
        if k < 2: time.sleep(20)
if todo:
    if not os.path.exists(AGY): sys.exit(f"agy 없음: {AGY}")
    batches = [todo[i:i + A.batch] for i in range(0, len(todo), A.batch)]
    with ThreadPoolExecutor(A.workers) as ex: list(ex.map(run, batches))
# text_scan.json — 지금 windows.json 전부를 캐시로 판정(--limit 이어도 캐시에 답이 있으면 scanned)
done = [all(k in R for k in WK[i]) for i in range(len(W))]
hast = [done[i] and any(R[k]["text"] for k in WK[i]) for i in range(len(W))]
what = [" / ".join(dict.fromkeys(R[k]["what"] for k in WK[i] if k in R and R[k]["text"] and R[k]["what"])) for i in range(len(W))]
SCN = merge([(s0(w), s0(w) + slen(w), "") for w, d in zip(W, done) if d])
TXT = merge([(s0(w), s0(w) + slen(w), t[:80]) for w, h, t in zip(W, hast, what) if h] + rows(MAN))
save_out({"scanned": [[a, b] for a, b, _ in SCN], "text": TXT, "manual": MAN, "made": datetime.datetime.now().isoformat(timespec="seconds"),
          "frames": len(R), **({"limit": A.limit} if A.limit else {})})
TW = [i for i in range(len(W)) if hast[i]]; TF_ = [i for i in TW if not W[i].get("noflip")]
print(f"보낸 프레임 {len(todo)} · 답 받은 프레임(누적) {len(R)} · 검사된 조각 {sum(done)}/{len(W)} · 글자 조각 {len(TW)} · 그중 지금 반전 {len(TF_)}"
      + (" → plan_v9 다시 짜면 noflip" if TF_ else ""))
for i in TF_[:20]: print(f"   w{i} 화면 {mm(W[i]['a'])} 원본 {mm(s0(W[i]))} 「{what[i][:50]}」")
miss = [i for i in SEND if not done[i]]
if miss:
    print(f"✗ 답 못 받은 조각 {len(miss)}개(프레임 못 뽑음 {len(nofr)} 포함) — textflip.py 다시(받은 답은 _tf/results.json 에 남음)")
    sys.exit(1)
