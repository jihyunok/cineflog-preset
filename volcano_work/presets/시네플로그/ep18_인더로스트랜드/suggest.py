# 나레 조각마다, 그 대사들 근처(±20초)에서 3초 간격에 안 걸리는 남은 자막 이벤트를 보여 준다(손으로 골라 넣기용)
import json, sys
EV = json.load(open("subev.json")); KO = json.load(open("ko18.json", encoding="utf-8"))
items = json.load(open("items.json", encoding="utf-8"))
D = [q for q in items if q["type"] == "D"]
used = {q["i"] for q in D if q["i"]}
def free(s, d): return all(s + d + 3.0 <= p["s"] or s >= p["s"] + p["d"] + 3.0 for p in D)
cur = None; blocks = []
for q in items:
    if q["type"] == "N": cur = [q, []]; blocks.append(cur)
    elif cur: cur[1].append(q)
for n, ds in blocks:
    ts = [q["s"] for q in ds if q["i"]]
    if not ts: continue
    a, b = min(ts) - 20, max(ts) + 20
    c = []
    for e in EV:
        if e["id"] in used or not (a <= e["s"] <= b): continue
        ln = min(max(e["e"] - e["s"] + 0.15, 1.0), 3.9)
        if free(e["s"] - 0.05, ln): c.append(f'{e["id"]}:{KO.get(str(e["id"]), "?")}')
    if c: print(n["ni"], n["text"][:22], "|", len(ds), "|", " / ".join(c))
