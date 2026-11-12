# -*- coding: utf-8 -*-
"""11-05 48 프로젝트 파워: 처음 보는 사람 검토용 글 두 개.
_timeline.txt  = 화면 순서대로 [나레] / [원본 대사 자막] / [원본 소리만] (줄거리 모르는 검토자는 이것만 읽는다)
_factsheet.txt = 위 + 줄마다 「그림: [원본N s] 컷 설명」 (사실·그림·잔혹 컷 검사용)
사용: 작업 폴더에서 python timeline_sheet.py [windows.json|windows_dry.json]"""
import json, sys, os
sys.stdout.reconfigure(encoding="utf-8")
WF = sys.argv[1] if len(sys.argv) > 1 else ("windows_dry.json" if os.path.exists("windows_dry.json") else "windows.json")
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
W = json.load(open(WF, encoding="utf-8"))
sh = json.load(open("shots.json", encoding="utf-8")) if os.path.exists("shots.json") else []
def d(t): return next((x["desc"] for x in sh if x["s"] <= t < x["e"]), "")
def mm(t): m = int(t // 60); return f"{m}:{t - 60 * m:04.1f}"
first = {}
for w in W: first.setdefault(w["k"], w["a"])
tl, fs = [], []
for k, x in enumerate(S):
    if x[0] == "ZONE": tl.append(f"===== {x[1]} ====="); fs.append(tl[-1]); continue
    t = first.get(k); ts = mm(t) if t is not None else "?"
    line = {"N": f"[나레] {x[1]}", "D": f"[원본 대사 자막] {x[2] if len(x) > 2 else ''}"}.get(x[0], "[원본 소리만, 자막 없음]")
    tl.append(f"{ts} {line}")
    pics = " / ".join(f"[원본{w['s']:.0f}s] {d(w['s'] + (w['b'] - w['a']) / 2)[:120]}" for w in W if w["k"] == k)
    fs.append(f"{ts} S{k} {line}\n      그림: {pics}")
open("_timeline.txt", "w", encoding="utf-8").write("\n".join(tl) + "\n")
open("_factsheet.txt", "w", encoding="utf-8").write("\n".join(fs) + "\n")
print("_timeline.txt", len(tl), "· _factsheet.txt")
