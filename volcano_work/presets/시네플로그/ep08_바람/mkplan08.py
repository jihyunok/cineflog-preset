# -*- coding: utf-8 -*-
"""한국어 원본 계획(08편): 대사 = ko.json 세그먼트 번호 → words.json 단어 시각(첫 단어-0.08 ~ 끝 단어+0.2)
(번호, 자막) / (번호, 자막, 시작 보정, 길이) / ("A", 시작, 길이). 대사끼리 원본 3초 간격 겹치면 뺀다."""
import json, sys, importlib
EP = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "ep08")
SEG = json.load(open("ko.json", encoding="utf-8")); W = json.load(open("words.json", encoding="utf-8"))
def span(n):
    s = SEG[n - 1]; ws = [w for w in W if s["s"] - 0.05 <= (w[0] + w[1]) / 2 <= s["e"] + 0.05]
    if not ws: return s["s"], s["e"]
    a = ws[0][0]; b = ws[-1][1]
    if ws[0][1] - ws[0][0] > 1.0: a = ws[0][1] - 0.55                # 첫 단어가 비정상으로 길면 앞 침묵을 뺀다
    if ws[-1][1] - ws[-1][0] > 1.2: b = ws[-1][0] + 0.6       # 끝 단어가 비정상으로 길면 자른다
    return a, b
items = []; rng = None; ni = 0; warn = []
for x in EP.S:
    if x[0] == "R": rng = [x[1], x[2]]; continue
    if x[0]: ni += 1; items.append({"type": "N", "ni": ni, "text": x[0], "rng": rng})
    if x[1] is None: continue
    for d in x[1]:
        if d[0] == "A":
            items.append({"type": "D", "i": 0, "s": round(d[1], 3), "d": round(min(d[2], 2.9), 2), "ko": "", "mirror": False}); continue
        n, ko = d[0], d[1]
        a, b = span(n)
        if len(d) >= 4: a = a + d[2]; b = a + d[3] - 0.28
        s0 = a - 0.08; ln = max(b + 0.2 - s0, 1.0); mirror = ln > 2.9
        if ln > 3.9: warn.append((n, ko, round(ln, 1)))
        items.append({"type": "D", "i": n, "s": round(s0, 3), "d": round(min(ln, 3.9 if mirror else 2.9), 2), "ko": ko, "mirror": mirror})
keep = []; drop = []; seen = set()
for q in items:
    if q["type"] == "D":
        if q["i"] and q["i"] in seen: drop.append(q["i"]); continue
        if any(not (q["s"] + q["d"] + 3.0 <= p["s"] or q["s"] >= p["s"] + p["d"] + 3.0) for p in keep if p["type"] == "D"):
            pv = keep[-1] if keep and keep[-1]["type"] == "D" else None   # 바로 앞 대사와 붙어 있으면 한 컷으로 합친다(좌우반전 ≤3.9초)
            if pv and pv["i"] and 0 <= q["s"] - pv["s"] and q["s"] + q["d"] - pv["s"] <= 3.9 and len(pv["ko"]) + len(q["ko"]) + 1 <= 24:
                others = [p for p in keep if p["type"] == "D" and p is not pv]
                ne = q["s"] + q["d"]
                if all(ne + 3.0 <= p["s"] or pv["s"] >= p["s"] + p["d"] + 3.0 for p in others):
                    pv["d"] = round(max(pv["d"], ne - pv["s"]), 2); pv["mirror"] = pv["d"] > 2.9; pv["ko"] += " " + q["ko"]; seen.add(q["i"]); continue
            drop.append(q["i"]); continue
        seen.add(q["i"])
    keep.append(q)
items = keep
bad = [q["ko"] for q in items if q["type"] == "D" and len(q["ko"]) > 24]
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
nch = sum(len(q["text"]) for q in items if q["type"] == "N"); dd = [q for q in items if q["type"] == "D"]
print("나레", ni, "조각", nch, "자 ≈", round(nch / 533, 1), "분 · 대사", len(dd), "개", round(sum(q["d"] for q in dd) / 60, 1), "분 · 뺀 대사", drop, "· 긴 자막", bad, "· 잘린 긴 대사", warn)
