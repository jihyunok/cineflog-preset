# -*- coding: utf-8 -*-
"""제브 대본 검사 (10-21 토큰 절약 ②: review_n·cold_read 대신 — 작업자·메인은 제브가 「틀림」으로 찍은 줄만 본다).
 사실: 나레 줄 ↔ 그 구간(앞뒤 40초) 원본 대사(srt.txt) — _제브/나레사실_맞음.json (contradicts)
 흐름: 앞서 들은 말(나레+대사 30줄) ↔ 이 나레 — _제브/나레흐름_막힘.json (unknown_reference · missing_cause)
결과: jev_fact_out.jsonl · jev_flow_out.jsonl → 화면에 걸린 줄(사실 0.6 · 모름 0.85 · 이유 0.75) + jev_check.txt.
 10-23 크래시 part1 시험: 사실 169줄 중 1(90% 0.35) · 흐름은 소개 줄도 0.8 대로 시끄러움.
 걸린 줄은 판정이 아니라 후보 — srt·그림으로 확인하고 고치거나 넘긴다.
 ★11-12 31v2: id 가 줄 번호(n001)뿐이라 글을 고친 뒤 다시 돌려도 _out.jsonl 의 옛 판정을 그대로 썼다(제브 거르기는 있는 id 를 건너뜀) → id 에 글·대사 해시를 붙여 고친 줄만 다시 판정.
사용: python jev_fact.py [--fact] [--flow] [--th 0.6]   (작업 폴더: script.py · srt.txt · lines.json)"""
import hashlib, json, os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
JEV = os.path.expanduser(r"~/volcano_work/_제브")
TH = float(sys.argv[sys.argv.index("--th") + 1]) if "--th" in sys.argv else 0.6
TH_REF, TH_CAUSE = 0.85, 0.75   # 흐름 판정은 시끄럽다(크래시 part1 169줄 시험: 모름 중앙 0.40·90% 0.82 — 소개하는 줄도 0.8 대) → 높은 문턱, 후보로만
DO = [m for m in ("fact", "flow") if f"--{m}" in sys.argv] or ["fact", "flow"]
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
SRT = []
for r in open("srt.txt", encoding="utf-8"):
    p = r.rstrip("\n").split("\t")
    if len(p) >= 4: SRT.append((float(p[1]), float(p[2]), p[3]))
def _flat(r):   # ★11-07 문장 구간(sent) 꼴: [(a,b), [(a,b),(a,b)], …] → (a,b) 목록
    return [q for e in r for q in (e if isinstance(e[0], (list, tuple)) else [e])]
def rng(x):
    if isinstance(x[2], (list, tuple)): r = _flat(x[2]); return min(a for a, _ in r), max(b for _, b in r)
    return x[2], x[3]
def dia(a, b, pad=40, cap=1400):
    t = " / ".join(s for s0, s1, s in SRT if s1 >= a - pad and s0 <= b + pad)
    return t[:cap]
rows = []; heard = []; n = 0
for k, x in enumerate(S):
    if x[0] == "N":
        n += 1; a, b = rng(x)
        rows.append({"k": k, "n": n, "text": x[1], "a": a, "b": b, "before": " | ".join(heard[-30:])})
        heard.append(x[1])
    elif x[0] == "D":
        heard.append("「" + x[2].replace(" / ", " ") + "」")
def run(spec, items, out):
    fi = out.replace("_out", "_in")
    with open(fi, "w", encoding="utf-8") as f:
        for it in items: f.write(json.dumps(it, ensure_ascii=False) + "\n")
    r = subprocess.run(["py", "-3.12", rf"{JEV}\거르기.py", "--spec", rf"{JEV}\{spec}", "--in", fi, "--out", out])
    if r.returncode == 2: print("★제브 거부(429·529)로 멈춤 — 잠시 뒤 다시 돌리면 이어서 함"); sys.exit(2)
    want = {it["id"] for it in items}   # ★11-12 31v2: 옛 결과(다른 글의 같은 번호)는 버림 — id 에 글 해시가 들어 있어 고친 줄만 다시 판정
    return {d["id"]: d["answers"] for d in map(json.loads, open(out, encoding="utf-8")) if d["id"] in want}
def hid(n, *parts): return f"n{n:03d}_" + hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()[:8]
R = {r["n"]: r for r in rows}; hits = []
if "fact" in DO:
    A = run("나레사실_맞음.json", [{"id": hid(r["n"], r["text"], dia(r["a"], r["b"])), "narration": r["text"], "dialogue": dia(r["a"], r["b"])} for r in rows], "jev_fact_out.jsonl")
    for i, v in A.items():
        if v["contradicts"] >= TH: hits.append((int(i[1:4]), "사실", v["contradicts"]))
if "flow" in DO:
    A = run("나레흐름_막힘.json", [{"id": hid(r["n"], r["before"], r["text"]), "before": r["before"] or "(nothing yet)", "line": r["text"]} for r in rows], "jev_flow_out.jsonl")
    for i, v in A.items():
        if v["unknown_reference"] >= TH_REF: hits.append((int(i[1:4]), "모름", v["unknown_reference"]))
        if v["missing_cause"] >= TH_CAUSE: hits.append((int(i[1:4]), "이유", v["missing_cause"]))
hits.sort()
out = [f"나레 {len(rows)}줄 · 걸림 {len(hits)} (문턱 {TH})"]
for n, kind, p in hits:
    r = R[n]; out.append(f"S{r['k']} n{n:03d} [{kind} {p:.2f}] {r['text']}  (원본 {r['a']:.0f}~{r['b']:.0f})")
open("jev_check.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
