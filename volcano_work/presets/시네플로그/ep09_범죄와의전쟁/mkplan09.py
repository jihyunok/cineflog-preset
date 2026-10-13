# -*- coding: utf-8 -*-
"""09편 계획: 대사 = ko.txt 줄 번호 → words.json 단어 시각으로 시작·끝 · 자막은 ep09.py 글자
ref: 번호 | (번호, "자막") | (번호, "자막", 길이) | ("A", 시작, 길이) = 자막 없는 원본 소리
사용: python mkplan09.py [--show]"""
import json, sys, importlib
EP = importlib.import_module("ep09")
W = json.load(open("words.json", encoding="utf-8")); SEG = json.load(open("ko.json", encoding="utf-8"))
SHOW = "--show" in sys.argv
def span(i):
    s = SEG[i - 1]
    ws = [w for w in W if s["s"] - 0.05 <= (w[0] + w[1]) / 2 <= s["e"] + 0.05]
    if not ws: return s["s"], s["e"], ""
    a = ws[0][0]; b = ws[-1][1]
    if ws[0][1] - ws[0][0] > 0.9: a = ws[0][1] - 0.6          # 첫 단어가 늘어난 경우
    if ws[-1][1] - ws[-1][0] > 1.0: b = ws[-1][0] + 0.7
    return a - 0.08, b + 0.2, " ".join(w[2] for w in ws)
items = []; rng = None; ni = 0
for x in EP.S:
    if x[0] == "R": rng = [x[1], x[2]]; continue
    if x[0]: ni += 1; items.append({"type": "N", "ni": ni, "text": x[0], "rng": rng})
    if x[1] is None: continue
    for d in x[1]:
        if isinstance(d, tuple) and d[0] == "A":
            items.append({"type": "D", "i": 0, "s": round(d[1], 3), "d": round(min(d[2], 2.9), 2), "ko": "", "mirror": False})
            if SHOW: print(f'    A {d[1]:8.2f} {d[2]:4.2f}  ||  ' + " ".join(w[2] for w in W if d[1] - 0.1 <= (w[0] + w[1]) / 2 <= d[1] + d[2] + 0.1))
            continue
        if isinstance(d, tuple) and d[0] == "T":                    # ("T", 시작, 길이, 자막) — 시각을 직접 준다(욕설 앞뒤 자르기)
            items.append({"type": "D", "i": 100000 + int(d[1] * 10), "s": round(d[1], 3), "d": round(d[2], 2), "ko": d[3], "mirror": d[2] > 2.9,
                          "said": " ".join(w[2] for w in W if d[1] <= (w[0] + w[1]) / 2 <= d[1] + d[2])}); continue
        if isinstance(d, int): d = (d, SEG[d - 1]["t"])
        a, b, said = span(d[0]); ln = b - a
        if len(d) > 2: ln = d[2]
        mirror = ln > 2.9; ln = min(ln, 3.9 if mirror else 2.9); ln = max(ln, 0.8)
        items.append({"type": "D", "i": d[0], "s": round(a, 3), "d": round(ln, 2), "ko": d[1], "mirror": mirror, "said": said})
        if SHOW: print(f'{d[0]:5d} {a:8.2f} {ln:4.2f} {"M" if mirror else " "} {d[1]}  ||  {said}')
# 같은 나레 뒤 이어지는 대사가 원본에서 3초 안에 붙어 있으면 한 컷으로 합친다(합친 길이 ≤3.9 좌우반전) — 자막은 "앞 / 뒤" 로 나눠 띄움
keep = []; drop = []; seen = set(); merged = 0
for q in items:
    if q["type"] == "D":
        if q["i"] and q["i"] in seen: continue
        prev = keep[-1] if keep and keep[-1]["type"] == "D" else None
        if prev and prev["i"] and q["i"] and q["s"] < prev["s"] + prev["d"] + 3.0 and q["s"] > prev["s"]:
            ne = q["s"] + q["d"]; tot = ne - prev["s"]
            if tot <= 3.9 and not any(not (ne + 3.0 <= p["s"] or prev["s"] >= p["s"] + p["d"] + 3.0) for p in keep[:-1] if p["type"] == "D"):
                cut = round(q["s"] - prev["s"], 2)
                prev["subs"] = prev.get("subs") or [[prev["ko"], 0.0]]
                prev["subs"].append([q["ko"], cut]); prev["ko"] = " / ".join(x[0] for x in prev["subs"])
                prev["d"] = round(tot, 2); prev["mirror"] = tot > 2.9; seen.add(q["i"]); merged += 1; continue
        if any(not (q["s"] + q["d"] + 3.0 <= p["s"] or q["s"] >= p["s"] + p["d"] + 3.0) for p in keep if p["type"] == "D"):
            drop.append((q["i"], q["ko"])); continue
        seen.add(q["i"])
    keep.append(q)
print("합친 대사", merged)
items = keep
bad = [x for q in items if q["type"] == "D" for x in ([s[0] for s in q["subs"]] if q.get("subs") else [q["ko"]]) if len(x) > 24]
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
nch = sum(len(q["text"]) for q in items if q["type"] == "N"); dd = [q for q in items if q["type"] == "D"]
print("나레", ni, "조각", nch, "자 ≈", round(nch / 533, 1), "분 · 대사", len(dd), "개", round(sum(q["d"] for q in dd) / 60, 1), "분 · 뺀 대사", drop, "· 긴 자막", bad)
