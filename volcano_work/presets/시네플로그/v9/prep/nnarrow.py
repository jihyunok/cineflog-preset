# -*- coding: utf-8 -*-
"""나레 문장마다 그 문장이 말하는 원본 구간 찾기 (11-07 33 콜래트럴 박제 「문장마다 원본 구간을 좁게(30초 안)」·「결과 먼저 금지」).
작업 폴더에서: 나레 줄의 문장마다(한국어 . ? ! 로 나눔, 영어는 narr_en.json 을 같은 수로 나눌 수 있으면 문장별) 옛 구간 ±15초 안 컷(shots.json)을
제브 나레그림_맞음(shows_narrated·contradicts)으로 판정 → 맞는 컷 묶음과 「허용 창」(앞 대사 원본 끝 ~ 뒤 대사 원본 시작) 안의 제안 구간.
허용 창 안에 맞는 컷이 없고 뒤 대사 뒤에만 있으면 「결과 먼저」 — 그 문장은 대사 뒤로 옮기거나 다시 쓴다.
사용: python nnarrow.py [k1 k2 …(대본 줄 번호, 없으면 전부)] → nnarrow.txt · nnarrow.json
★제안은 후보일 뿐 — 대본에 옮길 땐 그 구간 컷 설명·프레임으로 확인한다(전역 규칙: 보지 않은 것을 봤다고 쓰지 않는다)."""
import json, math, os, re, subprocess, sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
JEV = os.path.expanduser(r"~/volcano_work/_제브")
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
SH = json.load(open("shots.json", encoding="utf-8")); EN = json.load(open("narr_en.json", encoding="utf-8"))
ONLY = {int(x) for x in sys.argv[1:] if x.isdigit()}
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
def ssplit(t): return [x.strip() for x in re.split(r"(?<=[.?!…])\s+", t.strip()) if x.strip()]
IT = []; zone = "main"; ni = 0
for k, x in enumerate(S):
    if x[0] == "ZONE": zone = x[1]; continue
    opt = x[-1] if isinstance(x[-1], dict) else {}
    if x[0] == "N":
        ni += 1; rs = x[2] if isinstance(x[2], (list, tuple)) else [(x[2], x[3])]
        rs = [(min(float(q[0]) for q in r), max(float(q[1]) for q in r)) if isinstance(r[0], (list, tuple)) else (float(r[0]), float(r[1])) for r in rs]
        IT.append(dict(kind="N", k=k, ni=ni, zone=zone, text=x[1], opt=opt, rs=rs))
    elif x[0] == "D":
        ids = x[1] if isinstance(x[1], list) else [x[1]]
        s = min(L[i]["ws"] for i in ids if L[i]["ws"] is not None); e = max(L[i]["we"] for i in ids if L[i]["we"] is not None)
        IT.append(dict(kind="D", k=k, zone=zone, s=s, e=min(e + 1.5, s + 3.15), ko=x[2]))
    elif x[0] == "A": IT.append(dict(kind="A", k=k, zone=zone, s=float(x[1]), e=float(x[1]) + float(x[3]) * 1.05))
jobs = []; items = []
for i, it in enumerate(IT):
    if it["kind"] != "N" or it["zone"] == "outro" or it["opt"].get("cont") or (ONLY and it["k"] not in ONLY): continue
    pv = next((y for y in reversed(IT[:i]) if y["kind"] == "D" and y["zone"] == it["zone"]), None)
    nx = next((y for y in IT[i + 1:] if y["kind"] == "D" and y["zone"] == it["zone"]), None)
    lo_ok = pv["e"] + 3.0 if pv else 0.0; hi_ok = nx["s"] - 3.0 if nx else 1e9
    a0 = min(r[0] for r in it["rs"]); b0 = max(r[1] for r in it["rs"])
    c0, c1 = min(a0, lo_ok if pv else a0) - 15, max(b0, hi_ok if nx else b0) + 15
    c0 = max(c0, a0 - 120); c1 = min(c1, b0 + 120)
    ks = ssplit(it["text"]); es = ssplit(EN.get(str(it["ni"]), ""))
    if len(es) != len(ks): es = [EN.get(str(it["ni"]), it["text"])] * len(ks)
    w = f"narr/n{it['ni']:03d}.json"; al = json.load(open(w, encoding="utf-8")) if os.path.exists(w) else None
    tot = len(re.sub(r"\s", "", it["text"]))
    shots = [s for s in SH if s["e"] > c0 and s["s"] < c1 and s.get("desc")]
    J = dict(it=it, pv=pv, nx=nx, lo_ok=lo_ok, hi_ok=hi_ok, sents=[], shots=shots)
    for q, (ko, en) in enumerate(zip(ks, es)):
        sec = len(re.sub(r"\s", "", ko)) / 6.5
        if al and al.get("text") == it["text"] and len(al["chars"]) == len(it["text"]):
            p0 = it["text"].find(ko); p1 = p0 + len(ko) - 1
            if p0 >= 0: sec = al["en"][p1] - al["st"][p0]
        J["sents"].append(dict(q=q, ko=ko, en=en, sec=round(sec, 2)))
        for s in shots: items.append({"id": f"n{it['ni']:03d}_q{q}_{s['i']}", "narration": en, "shot": s["desc"]})
    jobs.append(J)
uniq = list({x["id"]: x for x in items}.values())
FI, FO = "_nn_in.jsonl", "_nn_out.jsonl"
old = {j["id"] for j in map(json.loads, open(FO, encoding="utf-8"))} if os.path.exists(FO) else set()
prev_in = {j["id"]: j for j in map(json.loads, open(FI, encoding="utf-8"))} if os.path.exists(FI) else {}
stale = {i for i in old if i in prev_in and any(x["id"] == i and x != prev_in[i] for x in uniq)}
if stale:   # 글이 바뀐 문장은 다시 판정
    keep = [l for l in open(FO, encoding="utf-8") if json.loads(l)["id"] not in stale]; open(FO, "w", encoding="utf-8").write("".join(keep))
with open(FI, "w", encoding="utf-8") as f:
    for x in {**prev_in, **{u["id"]: u for u in uniq}}.values(): f.write(json.dumps(x, ensure_ascii=False) + "\n")
print("판정할 문장×컷", len(uniq), "· 이미 있음", len(old) - len(stale), flush=True)
r = subprocess.run(["py", "-3.12", rf"{JEV}\거르기.py", "--spec", rf"{JEV}\나레그림_맞음.json", "--in", FI, "--out", FO])
R = {j["id"]: j["answers"] for j in map(json.loads, open(FO, encoding="utf-8"))}
def runs(xs):
    out = []
    for s0, s1, sc in sorted(xs):
        if out and s0 - out[-1][1] < 0.5: out[-1][1] = max(out[-1][1], s1); out[-1][2] = max(out[-1][2], sc)
        else: out.append([s0, s1, sc])
    return out
T = []; OUTJ = []
for J in jobs:
    it = J["it"]; nx = J["nx"]
    hdr = f"k{it['k']} n{it['ni']:03d} 「{it['text']}」 옛 {' '.join(f'[{mm(a)}~{mm(b)}]' for a, b in it['rs'])} · 허용 창 {mm(J['lo_ok'])}~{mm(J['hi_ok']) if nx else '끝'}" + (f" (뒤 대사 k{nx['k']} {mm(nx['s'])} 「{nx['ko'][:24]}」)" if nx else "")
    T.append(hdr); props = []; last = J["lo_ok"]
    for sq in J["sents"]:
        sc = [(s["s"], s["e"], R.get(f"n{it['ni']:03d}_q{sq['q']}_{s['i']}", {}).get("shows_narrated", 0) - R.get(f"n{it['ni']:03d}_q{sq['q']}_{s['i']}", {}).get("contradicts", 0), s) for s in J["shots"]]
        good = [(a, b, v) for a, b, v, _ in sc if v >= 0.3]
        rr = runs(good)
        inside = [x for x in rr if x[1] > max(last, J["lo_ok"]) + 1 and x[0] < J["hi_ok"] - 1]
        need = sq["sec"] * 1.05 + 0.4
        prop = None
        if inside:
            x = inside[0]; a = max(x[0], last, J["lo_ok"]); b = min(J["hi_ok"], max(x[1], a + need + 1.0), a + 30)
            prop = (round(a, 1), round(b, 1)); last = a
        after = [x for x in rr if x[0] >= J["hi_ok"] - 1]
        best = sorted(sc, key=lambda z: -z[2])[:3]
        T.append(f"  q{sq['q']} 「{sq['ko']}」 {sq['sec']:.1f}초 · 맞는 컷 묶음 " + (" ".join(f"{mm(a)}-{mm(b)}({v:.2f})" for a, b, v in rr[:6]) or "없음")
                 + (f" → 제안 [{mm(prop[0])}~{mm(prop[1])}]" if prop else " → ✗ 허용 창 안에 맞는 컷 없음") + (f" · 뒤 대사 뒤에 {len(after)}묶음(결과 먼저 의심)" if after and not prop else ""))
        for a, b, v, s in best: T.append(f"      {mm(a)} {v:+.2f} {s['desc'][:110]}")
        props.append(dict(q=sq["q"], ko=sq["ko"], sec=sq["sec"], prop=prop, runs=[(round(a, 1), round(b, 1), round(v, 2)) for a, b, v in rr]))
    OUTJ.append(dict(k=it["k"], ni=it["ni"], text=it["text"], lo_ok=J["lo_ok"], hi_ok=J["hi_ok"], next_k=nx["k"] if nx else None, sents=props))
open("nnarrow.txt", "w", encoding="utf-8").write("\n".join(T) + "\n")
json.dump(OUTJ, open("nnarrow.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("줄", len(jobs), "· 제안 없는 문장", sum(1 for j in OUTJ for s in j["sents"] if not s["prop"]), "→ nnarrow.txt")
