# -*- coding: utf-8 -*-
"""자막이 박힌 원본용 계획(07편 mkplan07 꼴) — 18편: 대사 번호 = 박힌 자막 이벤트 id(subev.json) 바로 · 글자 ko18.json · (id, "글자") 는 글자 바꿈
나레 뒤 대사 여러 줄 · ("A", 시작, 길이) 원본 소리 · 원본 3초 간격 겹치면 뺀다 · 글자 "X" = 쓰지 않음
★자막 한 줄 18자 안(글자 커짐 N84·D88) · 제목 낱말 검사
사용: python mkplan18.py ep18"""
import json, sys, importlib
EP = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "ep18")
EV = {e["id"]: e for e in json.load(open("subev.json"))}
KO = json.load(open("ko18.json", encoding="utf-8"))
MAXC = 18; BANNED = ["로스트", "랜드", "잃어버린 땅"]
items = []; rng = None; ni = 0; miss = []
for x in EP.S:
    if x[0] == "R": rng = [x[1], x[2]]; continue
    if x[0]: ni += 1; items.append({"type": "N", "ni": ni, "text": x[0], "rng": rng})
    if x[1] is None: continue
    for d in x[1]:
        if isinstance(d, tuple) and d[0] == "A":
            items.append({"type": "D", "i": 0, "s": round(d[1], 3), "d": round(min(d[2], 2.9), 2), "ko": "", "mirror": False}); continue
        if isinstance(d, tuple): eid, ko = d
        else:
            eid = d; ko = KO.get(str(eid))
            if ko is None: miss.append(eid); continue
        if ko == "X": continue
        e = EV[eid]
        ln = max(e["e"] - e["s"] + 0.15, 1.0); mirror = ln > 2.9
        items.append({"type": "D", "i": eid, "s": round(e["s"] - 0.05, 3), "d": round(min(ln, 3.9 if mirror else 2.9), 2), "ko": ko, "mirror": mirror})
keep = []; drop = []; seen = set()
for q in items:
    if q["type"] == "D":
        if q["i"] and q["i"] in seen: continue
        if any(not (q["s"] + q["d"] + 3.0 <= p["s"] or q["s"] >= p["s"] + p["d"] + 3.0) for p in keep if p["type"] == "D"):
            drop.append(q["i"] or ("A", q["s"])); continue
        if q["i"]: seen.add(q["i"])
    keep.append(q)
items = keep
bad = [q["ko"] for q in items if q["type"] == "D" and len(q["ko"]) > MAXC]
ttl = [q.get("text") or q.get("ko") for q in items if any(b in (q.get("text") or q.get("ko") or "") for b in BANNED)]
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
nch = sum(len(q["text"]) for q in items if q["type"] == "N"); dd = [q for q in items if q["type"] == "D"]
dmin = sum(q["d"] for q in dd) / 60
print("나레", ni, "조각", nch, "자 ≈", round(nch / 470, 1), "분(제미나이 Ludo 470자/분) · 대사", len(dd), "개", round(dmin, 1), "분 · 예상", round(nch / 470 + dmin, 1), "분")
print("뺀 대사", len(drop), drop)
print("긴 자막(>%d)" % MAXC, bad)
print("제목 낱말", ttl)
print("ko18.json 에 없는 id", miss)
