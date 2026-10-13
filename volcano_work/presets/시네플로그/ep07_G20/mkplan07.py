# -*- coding: utf-8 -*-
"""자막이 박힌 원본용 계획(05편): 대사 번호 = en.txt 줄 → need.json(박힌 자막 이벤트 id) → subev.json 시각 + ko07.json 글자
나레 뒤 대사 여러 줄 · ("A", 시작, 길이) 원본 소리 · 원본 3초 간격 겹치면 뺀다 · 글자 "X" = 쓰지 않음(선정적 대사 등)
사용: python mkplan05.py ep05"""
import json, sys, importlib
EP = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "ep07")
NEED = json.load(open("need.json")); EV = {e["id"]: e for e in json.load(open("subev.json"))}
KO = json.load(open("ko07.json", encoding="utf-8"))
items = []; rng = None; ni = 0
for x in EP.S:
    if x[0] == "R": rng = [x[1], x[2]]; continue
    if x[0]: ni += 1; items.append({"type": "N", "ni": ni, "text": x[0], "rng": rng})
    if x[1] is None: continue
    for d in x[1]:
        if isinstance(d, tuple):
            items.append({"type": "D", "i": 0, "s": round(d[1], 3), "d": round(min(d[2], 2.9), 2), "ko": "", "mirror": False}); continue
        eid = NEED[str(d)]; e = EV[eid]; ko = KO.get(str(eid), "X")
        if ko == "X": continue
        ln = max(e["e"] - e["s"] + 0.15, 1.0); mirror = ln > 2.9
        items.append({"type": "D", "i": eid, "s": round(e["s"] - 0.05, 3), "d": round(min(ln, 3.9 if mirror else 2.9), 2), "ko": ko, "mirror": mirror})
keep = []; drop = []; seen = set()
for q in items:
    if q["type"] == "D":
        if q["i"] and q["i"] in seen: continue
        if any(not (q["s"] + q["d"] + 3.0 <= p["s"] or q["s"] >= p["s"] + p["d"] + 3.0) for p in keep if p["type"] == "D"):
            drop.append(q["i"]); continue
        seen.add(q["i"])
    keep.append(q)
items = keep
bad = [q["ko"] for q in items if q["type"] == "D" and len(q["ko"]) > 24]
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
nch = sum(len(q["text"]) for q in items if q["type"] == "N"); dd = [q for q in items if q["type"] == "D"]
print("나레", ni, "조각", nch, "자 ≈", round(nch / 533, 1), "분 · 대사", len(dd), "개", round(sum(q["d"] for q in dd) / 60, 1), "분 · 뺀 대사", len(drop), "· 긴 자막", bad)
