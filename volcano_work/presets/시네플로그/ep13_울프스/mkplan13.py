# -*- coding: utf-8 -*-
"""자막이 박힌 원본용 계획(05편): 대사 번호 = en.txt 줄 → need.json(박힌 자막 이벤트 id) → subev.json 시각 + ko13.json 글자
나레 뒤 대사 여러 줄 · ("A", 시작, 길이) 원본 소리 · 원본 3초 간격 겹치면 뺀다 · 글자 "X" = 쓰지 않음(선정적 대사 등)
사용: python mkplan13.py ep13"""
import json, sys, importlib
EP = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "ep13")
NEED = json.load(open("need.json")); EV = {e["id"]: e for e in json.load(open("subev.json"))}
KO = json.load(open("ko13.json", encoding="utf-8"))
ADD = json.load(open("addev.json")) if __import__("os").path.exists("addev.json") else {}   # 대사 모자란 조각에 덧붙인 박힌 자막 이벤트(addcand.py)
def dev(eid):
    e = EV[eid]; ko = KO.get(str(eid), "X")
    if ko == "X": return None
    ln = max(e["e"] - e["s"] + 0.15, 1.0); mirror = ln > 2.9
    return {"type": "D", "i": eid, "s": round(e["s"] - 0.05, 3), "d": round(min(ln, 3.9 if mirror else 2.9), 2), "ko": ko, "mirror": mirror}
items = []; rng = None; ni = 0
for x in EP.S:
    if x[0] == "R": rng = [x[1], x[2]]; continue
    if x[0]: ni += 1; items.append({"type": "N", "ni": ni, "text": x[0], "rng": rng})
    if x[1] is None: continue
    for d in x[1]:
        if isinstance(d, tuple):
            items.append({"type": "D", "i": 0, "s": round(d[1], 3), "d": round(min(d[2], 2.9), 2), "ko": "", "mirror": False}); continue
        q = dev(NEED[str(d)])
        if q: items.append(q)
    if x[0] and str(ni) in ADD:
        for eid in ADD[str(ni)]:
            q = dev(eid)
            if q: items.append(q)
        k = max(j for j, q in enumerate(items) if q["type"] == "N") + 1
        items[k:] = sorted(items[k:], key=lambda q: q["s"])
keep = []; drop = []; seen = set()
for q in items:
    if q["type"] == "D":
        if q["i"] and q["i"] in seen: continue
        if any(not (q["s"] + q["d"] + 3.0 <= p["s"] or q["s"] >= p["s"] + p["d"] + 3.0) for p in keep if p["type"] == "D"):
            drop.append(q["i"]); continue
        seen.add(q["i"])
    keep.append(q)
items = keep
# 나레 한 조각 뒤 대사는 6줄까지(10-07 나레 줄임) — 넘으면 덧붙인 이벤트(ADD)부터, 그다음 뒤에서부터 뺀다
AD = set(i for v in ADD.values() for i in v); out = []; run = []
def flush():
    while len(run) > 6:
        j = next((k for k in range(len(run) - 1, -1, -1) if run[k]["i"] in AD), len(run) - 1); run.pop(j)
    out.extend(run); run.clear()
for q in items:
    if q["type"] == "N": flush(); out.append(q)
    else: run.append(q)
flush(); items = out
bad = [q["ko"] for q in items if q["type"] == "D" and len(q["ko"]) > 18]
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
nch = sum(len(q["text"]) for q in items if q["type"] == "N"); dd = [q for q in items if q["type"] == "D"]
print("나레", ni, "조각", nch, "자 ≈", round(nch / 410, 1), "분 · 대사", len(dd), "개", round(sum(q["d"] for q in dd) / 60, 1), "분 · 뺀 대사", len(drop), "· 긴 자막", bad)
