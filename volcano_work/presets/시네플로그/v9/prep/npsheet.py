# -*- coding: utf-8 -*-
"""관문 ⑨(제브 나레↔그림 어긋남) 조각 확인 시트 — 칸마다 id·화면·원본 시각, 한국어 나레, agy 그림 설명 + 조각 시작·가운데 프레임(완성본처럼 반전). 10-18 05v2
★11-07 다시 씀 (33 콜래트럴: 옛 판이 _gate_pre.log 의 id 를 다시 짠 windows.json 에 대어 IndexError — 시트 없이 38조각을 「눈으로 봄」 일괄 허용)
 - _gate_pre.log 안 씀: jev_np_in.jsonl + jev_np_out.jsonl 에서 관문 ⑨ 와 같은 조각(어긋남 ≥0.6 · 맞음 <0.3)을 고른다. --all-flagged = narr_pic 의 넓은 잣대(어긋남 ≥0.5 또는 맞음 <0.3)
 - id n{ni:03d}_w{j}_{a:.1f} 를 지금 windows.json 에 댄다: w[j] 가 있고 kind A · |화면 시작 − a| < 0.06 · 같은 나레 줄 밑. 하나라도 안 맞으면 exit 1(확인 표시 안 씀)
 - 다 만들면 _npsheet_ok.json {win_sig(windows.json sha1), ids, sheets, made} — gate ⑨ 허용은 이게 지금 windows.json 과 맞을 때만 된다
 - _npsheet_allow_template.json {id: {"seen": "", "sheet": …}} — 사람이 시트를 보고 seen(그 프레임에 보이는 것)을 조각마다 따로 적어 gate_allow.json 에 옮긴다(이 스크립트는 gate_allow.json 을 안 건드림)
사용: python npsheet.py [--all-flagged]   (작업 폴더) → npsheet_K.jpg (한 장 12조각, 줄마다 4)"""
import argparse, datetime, hashlib, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
ap = argparse.ArgumentParser(); ap.add_argument("--all-flagged", action="store_true"); A = ap.parse_args()
OK, TPL = "_npsheet_ok.json", "_npsheet_allow_template.json"
if os.path.exists(OK): os.remove(OK)                 # 옛 확인 표시는 먼저 지운다 — 이번에 끝까지 가야만 다시 생김
CFG = json.load(open("ep.json", encoding="utf-8")); SRC = CFG["src"]
WB = open("windows.json", "rb").read(); W = json.loads(WB.decode("utf-8")); SIG = hashlib.sha1(WB).hexdigest()
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
N = [x[1] for x in ns["S"] if x[0] == "N"]
kn = {}; ni = 0
for k, x in enumerate(ns["S"]):
    if x[0] == "N": ni += 1; kn[k] = ni
SH = json.load(open("shots.json", encoding="utf-8")) if os.path.exists("shots.json") else []
def desc(t): return next((x for x in SH if x["s"] <= t < x["e"]), {}).get("desc", "")
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
def slen(w): return (w["b"] - w["a"]) * w.get("rate", 1.05 if w["kind"] == "A" else 1.0)
def s0(w): return w["s"] - w.get("pre", 0)
JIN = {}
for l in open("jev_np_in.jsonl", encoding="utf-8"):
    if l.strip(): j = json.loads(l); JIN[j["id"]] = j
JOUT = [json.loads(l) for l in open("jev_np_out.jsonl", encoding="utf-8") if l.strip()]
def pick(a): return (a["contradicts"] >= 0.5 or a["shows_narrated"] < 0.3) if A.all_flagged else (a["contradicts"] >= 0.6 and a["shows_narrated"] < 0.3)
sel = list(dict.fromkeys(o["id"] for o in JOUT if pick(o["answers"])))
SC = {o["id"]: o["answers"] for o in JOUT}
RX = re.compile(r"^n(\d{3})_w(\d+)_(-?\d+\.\d)$")
P, badid = [], []
for i in sel:
    m = RX.match(i)
    if not m: badid.append((i, "id 꼴 아님")); continue
    n, j, a = int(m[1]), int(m[2]), float(m[3])
    if j >= len(W): badid.append((i, f"w{j} 없음(지금 조각 {len(W)}개)")); continue
    w = W[j]
    if w["kind"] != "A": badid.append((i, f"w{j} 가 {w['kind']} 조각")); continue
    if abs(w["a"] - a) >= 0.06: badid.append((i, f"w{j} 화면 시작 {w['a']:.2f} ≠ {a:.1f}")); continue
    if kn.get(w.get("k")) != n: badid.append((i, f"w{j} 는 나레 n{kn.get(w.get('k'))} 밑(id 는 n{n:03d})")); continue
    P.append({"id": i, "n": n, "j": j, "w": w})
print(f"⑨ 조각 {len(sel)}개 ({'넓은 잣대 --all-flagged' if A.all_flagged else '관문 ⑨ 잣대: 어긋남 ≥0.6 · 맞음 <0.3'}) · jev_np 판정 {len(JOUT)}")
if badid:
    print(f"✗ id {len(badid)}개가 지금 windows.json 과 안 맞음 — narr_pic.py 다시(제브 판정부터). 확인 표시(_npsheet_ok.json) 안 씀")
    for i, why in badid[:40]: print("   ", i, "—", why)
    sys.exit(1)
if not P: print("확인할 조각 없음"); sys.exit(0)
stale = [p["id"] for p in P if p["id"] in JIN and JIN[p["id"]].get("shot") and JIN[p["id"]]["shot"] != desc(s0(p["w"]) + slen(p["w"]) / 2)]
if stale: print(f"  (주의) {len(stale)}조각은 제브가 본 그림 설명과 지금 shots.json 설명이 다름 — {', '.join(stale[:5])}")

os.makedirs("_np", exist_ok=True)
def grab(tf):
    t, flip = tf; p = f"_np/{max(t, 0):.2f}_{int(flip)}.jpg"
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(t, 0):.3f}", "-i", SRC, "-frames:v", "1", "-vf", ("hflip," if flip else "") + "scale=400:-2", "-q:v", "3", p + ".tmp.jpg"])
        if os.path.exists(p + ".tmp.jpg"): os.replace(p + ".tmp.jpg", p)
    return p if os.path.exists(p) else None
for p in P:
    w = p["w"]; p["t0"] = s0(w) + 0.15; p["tm"] = s0(w) + slen(w) / 2; p["flip"] = not w.get("noflip")
jobs = [(p[k], p["flip"]) for p in P for k in ("t0", "tm")]
with ThreadPoolExecutor(8) as ex: got = list(ex.map(grab, jobs))
miss = [jb for jb, g in zip(jobs, got) if g is None]
if miss: print(f"✗ 프레임 {len(miss)}장 못 뽑음(원본 {', '.join(mm(t) for t, _ in miss[:5])}) — 확인 표시 안 씀"); sys.exit(1)
for i, p in enumerate(P): p["f0"], p["fm"] = got[2 * i], got[2 * i + 1]

FD = CFG.get("fonts", "fonts"); FP = f"{FD}/Cafe24Dangdanghae.ttf" if os.path.exists(f"{FD}/Cafe24Dangdanghae.ttf") else r"C:\Windows\Fonts\malgun.ttf"
F1, F2, F3, F4 = (ImageFont.truetype(FP, z) for z in (17, 18, 14, 13))
def wrap(t, f, wmax, nmax):
    out, cur = [], ""
    for wd in t.split():
        while f.getlength(wd) > wmax:                     # 너무 긴 낱말은 글자 단위로
            k = len(wd)
            while k > 1 and f.getlength(wd[:k]) > wmax: k -= 1
            if cur: out.append(cur); cur = ""
            out.append(wd[:k]); wd = wd[k:]
        if not cur: cur = wd
        elif f.getlength(cur + " " + wd) <= wmax: cur += " " + wd
        else: out.append(cur); cur = wd
    if cur: out.append(cur)
    if len(out) > nmax: out = out[:nmax]; out[-1] = out[-1][:max(1, len(out[-1]) - 1)] + "…"
    return out
C, CW, GAP, PER = 4, 400, 6, 12
FH = Image.open(P[0]["f0"]).size[1]; HEAD = 4 + 22 + 3 * 22 + 3 * 17 + 4; TH = HEAD + 2 * FH + 2
sheets = []
for b in range(0, len(P), PER):
    part = P[b:b + PER]; rows = (len(part) + C - 1) // C
    im = Image.new("RGB", (C * CW + (C - 1) * GAP, rows * TH + (rows - 1) * GAP), (60, 60, 60)); d = ImageDraw.Draw(im)
    for i, p in enumerate(part):
        x0, y0 = (i % C) * (CW + GAP), (i // C) * (TH + GAP); w = p["w"]
        d.rectangle([x0, y0, x0 + CW - 1, y0 + HEAD - 1], fill=(18, 18, 18))
        sc = SC.get(p["id"], {})
        d.text((x0 + 4, y0 + 3), f"{p['id']}  화면 {mm(w['a'])}  원본 {mm(s0(w))}" + ("" if p["flip"] else "  반전X"), font=F1, fill=(255, 220, 0))
        y = y0 + 26
        for ln in wrap(N[p["n"] - 1] if p["n"] - 1 < len(N) else "(나레 없음)", F2, CW - 8, 3): d.text((x0 + 4, y), ln, font=F2, fill=(255, 255, 255)); y += 22
        y = y0 + 26 + 3 * 22
        for ln in wrap(f"제브 어긋남 {sc.get('contradicts', 0):.2f}·맞음 {sc.get('shows_narrated', 0):.2f} | agy: " + desc(p["tm"]), F3, CW - 8, 3): d.text((x0 + 4, y), ln, font=F3, fill=(150, 210, 255)); y += 17
        for k, (key, lab, t) in enumerate((("f0", "시작", p["t0"]), ("fm", "가운데", p["tm"]))):
            fy = y0 + HEAD + k * (FH + 2); im.paste(Image.open(p[key]).convert("RGB").resize((CW, FH)), (x0, fy))
            d.rectangle([x0, fy, x0 + 118, fy + 16], fill=(0, 0, 0)); d.text((x0 + 3, fy + 1), f"{lab} 원본 {mm(t)}", font=F4, fill=(255, 255, 0))
    nm = f"npsheet_{b // PER}.jpg"; im.save(nm, quality=85); sheets.append(nm)
    for p in part: p["sheet"] = nm
if not all(os.path.exists(s) for s in sheets): print("✗ 시트 저장 실패 — 확인 표시 안 씀"); sys.exit(1)
for f in os.listdir("."):                               # 지난번 남은 시트(번호가 더 큰 것) 지움 — 옛 시트를 보지 않게
    if re.fullmatch(r"npsheet_\d+\.jpg", f) and f not in sheets: os.remove(f)
json.dump({"win_sig": SIG, "ids": [p["id"] for p in P], "sheets": sheets, "all_flagged": A.all_flagged,
           "made": datetime.datetime.now().isoformat(timespec="seconds")}, open(OK, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
T = json.load(open(TPL, encoding="utf-8")) if os.path.exists(TPL) else {}
for p in P:
    e = T.get(p["id"]) if isinstance(T.get(p["id"]), dict) else {}
    T[p["id"]] = {"seen": e.get("seen", ""), "sheet": p["sheet"]}
json.dump(T, open(TPL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(P)} 조각 · 시트 {len(sheets)}장 ({', '.join(sheets)}) · {OK} · {TPL}")
print("할 일(사람이 눈으로): 시트를 열어 조각마다 시작·가운데 프레임에 실제로 보이는 것(인물·장소·물건·행동)을 템플릿 seen 에 따로 적는다.\n"
      "  나레와 맞는 조각만 gate_allow.json 에 옮긴다(12자+ · 조각마다 다른 글 — 같은 문구는 관문이 거절). 안 맞으면 나레 원본 구간을 고친다.\n"
      "  windows.json 이 바뀌면 이 확인은 무효 — narr_pic.py → npsheet.py 다시.")
