# -*- coding: utf-8 -*-
"""plan 「자리 없음」 나레 줄 → 앞뒤 빈 자리로 구간 자동 넓히기(10-31 대작 15B·16).
작업 폴더에서 plan_v9 를 돌린 뒤: python autowiden.py [최대초=8]
- plan.log 의 「✗ 줄N N 「글」 … 놓을 자리 없음」 줄마다, windows.json 의 다른 조각(±3초 간격)과 ep.json avoid 를 피해
  그 줄 구간을 앞뒤로 최대 N초까지 넓힌 값을 _widen.json {나레 글: [a, b]} 에 더한다(이미 있으면 덮어씀).
- _post_merge.py 에 아래 두 줄이 있어야 반영된다(없으면 이 도구가 끝에 붙여 줌):
    _W = json.load(open("_widen.json")) → S 의 N 줄 구간을 _W 값으로 바꿈
- 넓혀도 모자라면(이웃 대사가 막음) 「막는 이웃」을 찍어 준다. `--drop` 이면 원본 시각이 가장 가까운 이웃 대사 하나를 _drop.json 에 넣어 빼고 그 자리까지 넓힌다(아니면 _speedfit 으로 녹음을 줄임).
넓힌 구간은 그림이 바뀔 수 있으니 narr_pic·관문 ⑨ 시트로 꼭 다시 본다."""
import json, os, re, sys
args = [a for a in sys.argv[1:] if not a.startswith("--")]
MAXW = float(args[0]) if args else 8.0
DROP = "--drop" in sys.argv
log = open("plan.log", encoding="utf-8").read()
W = json.load(open("windows.json", encoding="utf-8"))
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
ep = json.load(open("ep.json", encoding="utf-8"))
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
iv = [(w["s"], w["s"] + (w["b"] - w["a"]) * w.get("rate", 1.0)) for w in W]
iv += [(a, b) for a, b in ep.get("avoid", [])]
wd = json.load(open("_widen.json", encoding="utf-8")) if os.path.exists("_widen.json") else {}
drop = json.load(open("_drop.json", encoding="utf-8")) if os.path.exists("_drop.json") else []
def rng(x):
    r = x[2] if isinstance(x[2], list) else [(x[2], x[3])]
    return min(p for p, q in r), max(q for p, q in r)
def srcr(x):
    if x[0] == "D":
        ids = x[1] if isinstance(x[1], list) else [x[1]]; return L[ids[0]]["s"], L[ids[-1]]["e"]
    if x[0] == "A": return x[1], x[2]
    return rng(x)
fails = re.findall(r"✗ 줄\d+ N 「([^」]+)」[^\n]*?(?:자리 없음|짧음)[^\n]*?필요 약 ([\d.]+)초", log)
for t, need in fails:
    i = next(j for j, y in enumerate(S) if y[0] == "N" and y[1].startswith(t)); y = S[i]
    a, b = rng(y)
    G = ep.get("tail_gap", 3.0) if a >= (ep.get("tail_src") or [1e18])[0] else 3.0     # 10-31 드루와 09: 꼬리 구간은 plan_v9 처럼 간격 tail_gap
    lo = max([e for s, e in iv if e <= a + 0.5] + [a - MAXW - G]) + G
    hi = min([s for s, e in iv if s >= b - 0.5] + [b + MAXW + G]) - G
    na, nb = round(min(a, max(lo, a - MAXW)), 1), round(max(b, min(hi, b + MAXW)), 1)
    wd[y[1]] = [na, nb]
    ok = (nb - na) >= float(need)
    nb_ = [(j, S[j][0], S[j][2] if S[j][0] == "D" else S[j][1]) for j in (i - 1, i + 1) if 0 <= j < len(S) and S[j][0] in ("D", "A")]
    if DROP and not ok:   # --drop: 원본 시각으로 가장 가까운 이웃 대사 하나를 빼서 자리 확보(_drop.json)
        cands = [(abs((srcr(S[j])[0] + srcr(S[j])[1]) / 2 - (a + b) / 2), j) for j in (i - 1, i + 1) if 0 <= j < len(S) and S[j][0] == "D"]
        if cands:
            j = min(cands)[1]; drop.append(S[j][2]); da, db = srcr(S[j])
            if db <= a + 0.5: na = round(max(da, a - MAXW), 1)
            else: nb = round(min(db, b + MAXW), 1)
            wd[y[1]] = [na, nb]; print("   → 이웃 대사 뺌:", S[j][2], "· 구간", (na, nb))
    print(("✓" if ok else "✗ 모자람"), y[1][:24], (round(a, 1), round(b, 1)), "→", (na, nb), "필요", need, "" if ok else f"· 막는 이웃 {nb_}")
json.dump(wd, open("_widen.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
if drop: json.dump(drop, open("_drop.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
pm = open("_post_merge.py", encoding="utf-8").read() if os.path.exists("_post_merge.py") else "# -*- coding: utf-8 -*-\n"
if "_widen.json" not in pm:
    pm += ('\n# autowiden.py — plan 「자리 없음」 줄 구간 넓힘 + 막는 이웃 대사 빼기\nimport json as _json, os as _os\n'
           '_W = _json.load(open("_widen.json", encoding="utf-8")) if _os.path.exists("_widen.json") else {}\n'
           'S = [(("N", x[1]) + tuple(_W[x[1]]) + tuple(y for y in x[2:] if isinstance(y, dict))) if x[0] == "N" and x[1] in _W else x for x in S]\n'
           '_D = _json.load(open("_drop.json", encoding="utf-8")) if _os.path.exists("_drop.json") else []\n'
           'S = [x for x in S if not (x[0] == "D" and x[2] in _D)]\n')
    open("_post_merge.py", "w", encoding="utf-8").write(pm); print("_post_merge.py 에 _widen.json·_drop.json 반영 줄 붙임")
