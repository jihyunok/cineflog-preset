# -*- coding: utf-8 -*-
"""ep11.S → items.json — mkplan04 + SDH 자막 정리((화자)·[소리]·"- " 지움) + 욕설 대사 검사(빼고 알림)
사용: python mkplan11.py ep11"""
import json, re, sys, importlib
EP = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "ep11")
S = json.load(open("subs_ko.json", encoding="utf-8"))
BAD = re.compile("씨발|씨벌|씨불|씨바|개새끼|새끼|지랄|염병|니미|병신|옘병|썅|지미|좆|뒤져|등신")
TITLE = re.compile("거룩|계보")
def clean(x):
    x = re.sub(r"\[[^\]]*\]", "", x); x = re.sub(r"\([^)]*\)", "", x)
    x = re.sub(r"(^|\s)- ", " ", x).replace("…", "..")
    return re.sub(r"\s+", " ", x).strip().strip("'\"")
def text(i, d=None):
    if d and len(d) > 1: return d[1]
    return getattr(EP, "SHORT", {}).get(i) or clean(S[i - 1]["t"])
def mk(i, d=None):
    q = S[i - 1]; nx = S[i]["s"] if i < len(S) else 1e9
    ln = max(min(q["e"] - q["s"] + 0.25, nx - q["s"] - 0.05), 1.0)
    if d and len(d) > 2: ln = d[2]
    mirror = ln > 2.9
    return {"type": "D", "i": i, "s": round(q["s"] - 0.05, 3), "d": round(min(ln, 3.9 if mirror else 2.9), 2), "ko": text(i, d), "mirror": mirror}
items = []; rng = None; ni = 0; swear = []
for x in EP.S:
    if x[0] == "R": rng = [x[1], x[2]]; continue
    if x[0]:
        ni += 1; items.append({"type": "N", "ni": ni, "text": x[0], "rng": rng})
    ds = x[1]
    if ds is None: continue
    for d in ds:
        if isinstance(d, tuple) and d[0] == "A":
            items.append({"type": "D", "i": 0, "s": round(d[1], 3), "d": round(min(d[2], 2.9), 2), "ko": "", "mirror": False}); continue
        d = d if isinstance(d, tuple) else (d,)
        must = d[0] < 0
        if must: d = (-d[0],) + tuple(d[1:])
        q = mk(d[0], d); q["must"] = must
        if not q["ko"] or BAD.search(q["ko"]) or BAD.search(clean(S[d[0] - 1]["t"])): swear.append((d[0], clean(S[d[0] - 1]["t"]))); continue
        items.append(q)
def clash(q, ks): return any(not (q["s"] + q["d"] + 3.0 <= p["s"] or q["s"] >= p["s"] + p["d"] + 3.0) for p in ks if p["type"] == "D")
import os
NOSUB = os.environ.get('NOSUB') == '1'
keep = []; drop = []; subs = 0
musts = []
for q in items:
    if q.get("must") and not clash(q, musts): musts.append(q)
for q in items:
    if q.get("must") and q in musts: keep.append(q); continue
    if q["type"] != "D" or not clash(q, keep + [m for m in musts if m not in keep]): keep.append(q); continue
    alt = None
    if q["i"] and not NOSUB:
        for k in (1, 2, -1, 3, -2, 4):
            j = q["i"] + k
            if 1 <= j <= len(S) and abs(S[j - 1]["s"] - q["s"]) < 20 and j not in {p.get("i") for p in keep}:
                c = mk(j)
                if c["ko"] and len(c["ko"]) <= 24 and not BAD.search(clean(S[j - 1]["t"])) and not clash(c, keep): alt = c; break
    if alt: keep.append(alt); subs += 1
    else: drop.append(q)
items = keep
bad = 0
for q in items:
    if q["type"] == "D" and len(q["ko"]) > 24: print("김", q["i"], q["ko"]); bad += 1
    s = q.get("ko") or q.get("text") or ""
    if TITLE.search(s): print("제목!", s); bad += 1
for q in items: q.pop("must", None)
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
nch = sum(len(q["text"]) for q in items if q["type"] == "N")
dd = [q for q in items if q["type"] == "D"]
print("욕설로 뺀 줄", swear)
print("뺀 줄:", [(q["i"], q["ko"]) for q in drop])
print("나레", ni, "조각", nch, "자 ≈", round(nch / 533, 1), "분 · 대사", len(dd), "개", round(sum(q["d"] for q in dd) / 60, 1), "분 · 바꿔 낀", subs, "· 뺀 대사", len(drop), [q["i"] for q in drop], "· 문제", bad)
