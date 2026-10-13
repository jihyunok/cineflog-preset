# -*- coding: utf-8 -*-
"""한국어 원본(받아쓰기 ko.json·words.json)용 계획 — 10편
대사 = ko.txt 줄 번호 | (번호, "자막") | (번호, "자막", 단어시작오프셋초, 길이) | ("A", 시작, 길이) 자막 없는 원본 소리
시각: 그 줄에 든 첫 단어 시작-0.08 ~ 마지막 단어 끝+0.2 · ≤2.9초(넘으면 좌우반전 ≤3.9) · 대사끼리 원본 3초 간격
사용: python mkplan10.py ep10"""
import json, sys, importlib
EP = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "ep10")
SEG = json.load(open("ko.json", encoding="utf-8")); W = json.load(open("words.json", encoding="utf-8"))
def words_of(i):
    s = SEG[i - 1]
    ws = [w for w in W if s["s"] - 0.05 <= (w[0] + w[1]) / 2 <= s["e"] + 0.05]
    return ws, s
items = []; rng = None; ni = 0; rep = []
for x in EP.S:
    if x[0] == "R": rng = [x[1], x[2]]; continue
    if x[0]: ni += 1; items.append({"type": "N", "ni": ni, "text": x[0], "rng": rng})
    if x[1] is None: continue
    for d in x[1]:
        if isinstance(d, tuple) and d[0] == "A":
            items.append({"type": "D", "i": 0, "s": round(d[1], 3), "d": round(min(d[2], 2.9), 2), "ko": "", "mirror": False}); continue
        if isinstance(d, int): d = (d, None)
        n, ko = d[0], d[1]
        ws, s = words_of(n)
        if not ko: ko = s["t"].strip().rstrip(".")
        if ws:
            # 자막 글자와 가장 닮은 연속 단어 묶음(길이 ≤3.9초)을 고른다 — 긴 줄에서 그 말만 잘라 쓰기
            import difflib
            key = ko.replace(" ", ""); best = None
            for i0 in range(len(ws)):
                for i1 in range(i0, len(ws)):
                    a0 = ws[i0][0]; e1 = ws[i1][1] if ws[i1][1] - ws[i1][0] <= 1.2 else ws[i1][0] + 0.9
                    if e1 - a0 > 3.7: break
                    txt = "".join(w[2] for w in ws[i0:i1 + 1]).replace(" ", "")
                    sc = difflib.SequenceMatcher(None, key, txt).ratio()
                    if best is None or sc > best[0] + 1e-9: best = (sc, a0, e1)
            a = best[1] - 0.08; b = best[2] + 0.2
        else:
            a = s["s"]; b = s["e"]
        ln = max(b - a, 0.8); mirror = ln > 2.9
        items.append({"type": "D", "i": n, "s": round(a, 3), "d": round(min(ln, 3.9 if mirror else 2.9), 2), "ko": ko, "mirror": mirror})
        rep.append(f'{n}\t{a:.2f}\t{ln:.2f}\t{ko}\t| {" ".join(w[2] for w in ws)}')
keep = []; drop = []; seen = set()
for q in items:
    if q["type"] == "D":
        if q["i"] and q["i"] in seen: continue
        if any(not (q["s"] + q["d"] + 3.0 <= p["s"] or q["s"] >= p["s"] + p["d"] + 3.0) for p in keep if p["type"] == "D"):
            drop.append(q["i"]); continue
        if q["i"]: seen.add(q["i"])
    keep.append(q)
items = keep
bad = [q["ko"] for q in items if q["type"] == "D" and len(q["ko"]) > 24]
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
open("dlist.txt", "w", encoding="utf-8").write("\n".join(rep))
nch = sum(len(q["text"]) for q in items if q["type"] == "N"); dd = [q for q in items if q["type"] == "D"]
print("나레", ni, "조각", nch, "자 ≈", round(nch / 533, 1), "분 · 대사", len(dd), "개", round(sum(q["d"] for q in dd) / 60, 1), "분 · 뺀 대사", len(drop), drop, "· 긴 자막", bad)
