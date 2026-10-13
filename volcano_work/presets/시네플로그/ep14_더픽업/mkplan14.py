# -*- coding: utf-8 -*-
"""epNN.S → items.json — 04편부터: 나레 뒤 대사 여러 줄 · 자막 없는 원본 소리 컷("A", 시작, 길이) · 나레 "" 이면 대사만
사용: python mkplan04.py ep04   (작업 폴더에 subs_ko.json, epNN.py)"""
import json, re, sys, importlib
EP = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "ep04")
S = json.load(open("subs_ko.json", encoding="utf-8"))
items = []; rng = None; ni = 0
for x in EP.S:
    if x[0] == "R": rng = [x[1], x[2]]; continue
    if x[0]:
        ni += 1; items.append({"type": "N", "ni": ni, "text": x[0], "rng": rng})
    ds = x[1]
    if ds is None: continue
    if not isinstance(ds, list): ds = [ds]
    for d in ds:
        if isinstance(d, tuple) and d[0] == "A":                       # 원본 소리만(자막 없음)
            ln = min(d[2], 2.9)
            items.append({"type": "D", "i": 0, "s": round(d[1], 3), "d": round(ln, 2), "ko": "", "mirror": False}); continue
        d = d if isinstance(d, tuple) else (d,)
        i = d[0]; q = S[i - 1]; nx = S[i]["s"] if i < len(S) else 1e9
        txt = d[1] if len(d) > 1 else getattr(EP, "SHORT", {}).get(i, q["t"])
        txt = re.sub(r"^- ", "", txt).replace(" - ", " ").strip("'\"").replace("…", "..")
        ln = min(q["e"] - q["s"] + 0.25, nx - q["s"] - 0.05)
        if len(d) > 2: ln = d[2]
        ln = max(ln, 1.0)
        mirror = ln > 2.9
        ln = min(ln, 3.9 if mirror else 2.9)
        items.append({"type": "D", "i": i, "s": round(q["s"] - 0.05, 3), "d": round(ln, 2), "ko": txt, "mirror": mirror})
# 대사끼리 원본 3초 간격 — 너무 가까우면 가까운 다른 줄(±1~4, 같은 장면 20초 안)로 바꾸고, 없으면 뺀다
def clash(q, ks): return any(not (q["s"] + q["d"] + 3.0 <= p["s"] or q["s"] >= p["s"] + p["d"] + 3.0) for p in ks if p["type"] == "D")
def mk(i):
    q = S[i - 1]; nx = S[i]["s"] if i < len(S) else 1e9
    txt = getattr(EP, "SHORT", {}).get(i, q["t"]); txt = re.sub(r"^- ", "", txt).replace(" - ", " ").strip("'\"").replace("…", "..")
    ln = max(min(q["e"] - q["s"] + 0.25, nx - q["s"] - 0.05), 1.0); mirror = ln > 2.9
    return {"type": "D", "i": i, "s": round(q["s"] - 0.05, 3), "d": round(min(ln, 3.9 if mirror else 2.9), 2), "ko": txt, "mirror": mirror}
keep = []; drop = []; subs = 0
for q in items:
    if q["type"] != "D": keep.append(q); continue
    if not clash(q, keep): keep.append(q); continue
    alt = None
    if q["i"]:
        for k in (1, 2, -1, 3, -2, 4):
            j = q["i"] + k
            if 1 <= j <= len(S) and abs(S[j - 1]["s"] - q["s"]) < 20 and j not in {p.get("i") for p in keep}:
                c = mk(j)
                if len(c["ko"]) <= 18 and not clash(c, keep): alt = c; break
    if alt: keep.append(alt); subs += 1
    else: drop.append(q)
items = keep
bad = 0
for q in items:
    if q["type"] == "D" and len(q["ko"]) > 18: print("김", q["i"], q["ko"]); bad += 1
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
nch = sum(len(q["text"]) for q in items if q["type"] == "N")
dd = [q for q in items if q["type"] == "D"]
print("나레", ni, "조각", nch, "자 ≈", round(nch / 410, 1), "분 · 대사", len(dd), "개", round(sum(q["d"] for q in dd) / 60, 1), "분 · 뺀 대사", len(drop), [q["i"] for q in drop], "· 문제", bad)
