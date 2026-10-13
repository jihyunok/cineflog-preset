# -*- coding: utf-8 -*-
"""한국어 원본 계획(08·12편): 대사 = ko.txt 줄 번호 + 사람이 고친 자막. 시각 = words.json 단어(첫 단어 시작-0.08 ~ 끝 단어 끝+0.2)
(번호, "자막"[, 최대 길이]) · ("A", 시작, 길이) 원본 소리 · 대사끼리 원본 3초 간격 겹치면 뺀다
사용: python mkplan12.py ep12"""
import json, sys, importlib
EP = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "ep12")
SEG = json.load(open("ko.json", encoding="utf-8")); W = json.load(open("words.json", encoding="utf-8"))
def span(n):
    s = SEG[n - 1]; ws = [w for w in W if s["s"] - 0.05 <= (w[0] + w[1]) / 2 <= s["e"] + 0.05]
    if not ws: return s["s"], s["e"]
    ws = [(max(w0, w1 - 0.7), w1, t) for w0, w1, t in ws]      # 한 단어가 1초 넘게 늘어지면(속삭임·침묵 포함) 끝 0.7초만 말로 본다
    a = ws[0][0]; b = ws[-1][1]
    # 단어 사이 1.2초 넘게 비면 덩어리를 나눠 말이 가장 많은 덩어리를 쓴다
    cl = [[ws[0]]]
    for w in ws[1:]:
        if w[0] - cl[-1][-1][1] > 1.2: cl.append([w])
        else: cl[-1].append(w)
    if len(cl) > 1:
        c = max(cl, key=lambda c: sum(len(w[2]) for w in c)); a = c[0][0]; b = c[-1][1]
    if b - ws[-1][0] > 1.2: b = ws[-1][0] + 0.6       # 마지막 단어 끝이 늘어진 경우
    return a, b
items = []; rng = None; ni = 0; warn = []
for x in EP.S:
    if x[0] == "R": rng = [x[1], x[2]]; continue
    if x[0]: ni += 1; items.append({"type": "N", "ni": ni, "text": x[0], "rng": rng})
    if x[1] is None: continue
    for d in x[1]:
        if d[0] == "A":
            items.append({"type": "D", "i": 0, "s": round(d[1], 3), "d": round(min(d[2], 2.9), 2), "ko": "", "mirror": False}); continue
        n, ko = d[0], d[1]; cap = d[2] if len(d) > 2 else None
        a, b = span(n); s0 = max(0, a - 0.08); ln = b + 0.2 - s0
        if ln < 1.5: s0 = max(0, s0 - 0.2); ln = 1.5          # 너무 짧으면 앞뒤를 조금 늘린다(단어 시각이 빠듯함)
        if cap: ln = min(ln, cap)
        if ln > 3.9: warn.append((n, round(ln, 1), ko))
        mirror = ln > 2.9
        items.append({"type": "D", "i": n, "s": round(s0, 3), "d": round(max(min(ln, 3.9 if mirror else 2.9), 0.9), 2), "ko": ko, "mirror": mirror})
keep = []; drop = []; seen = set()
for q in items:
    if q["type"] == "D":
        q["subs"] = [[q["ko"], 0.0]] if q["ko"] else []
        if q["i"] and q["i"] in seen: continue
        p = keep[-1] if keep else None
        # 바로 앞 대사와 원본에서 이어져 있으면(3초 안) 한 컷으로 합친다 — 합쳐서 3.9초 이하(넘으면 좌우반전)
        if p and p["type"] == "D" and p["ko"] and q["ko"] and 0 <= q["s"] - (p["s"] + p["d"]) < 3.0 and q["s"] + q["d"] - p["s"] <= 3.9:
            p["subs"].append([q["ko"], round(q["s"] - p["s"], 2)]); p["d"] = round(q["s"] + q["d"] - p["s"], 2)
            p["mirror"] = p["d"] > 2.9; seen.add(q["i"]); continue
        if any(not (q["s"] + q["d"] + 3.0 <= p["s"] or q["s"] >= p["s"] + p["d"] + 3.0) for p in keep if p["type"] == "D"):
            drop.append(q["i"]); continue
        seen.add(q["i"])
    keep.append(q)
items = keep
bad = [q["ko"] for q in items if q["type"] == "D" and len(q["ko"]) > 24]
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
nch = sum(len(q["text"]) for q in items if q["type"] == "N"); dd = [q for q in items if q["type"] == "D"]
print("나레", ni, "조각", nch, "자 ≈", round(nch / 533, 1), "분 · 대사", len(dd), "개", round(sum(q["d"] for q in dd) / 60, 1), "분 · 뺀 대사", drop, "· 긴 자막", bad)
print("3.9초 넘어 잘림:", warn)
