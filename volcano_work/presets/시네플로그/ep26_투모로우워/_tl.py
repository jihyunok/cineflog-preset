# -*- coding: utf-8 -*-
"""시간표 _tl.txt (컷 설명 ## + 대사 줄 id[✗] 시각 박힌 자막) · lines_ko.txt — 25편 _tl 꼴. 박힌 자막 srt.txt(ko_ocr) 를 시각으로 붙임. 10-28"""
import json
S = json.load(open("shots.json", encoding="utf-8")); L = json.load(open("lines.json", encoding="utf-8"))
K = [(float(a), float(b), t) for _, a, b, t in (r.rstrip("\n").split("\t", 3) for r in open("srt.txt", encoding="utf-8"))]
dc = {}
for row in open("dcand.txt", encoding="utf-8"):
    p = row.split("|")
    if p[0].strip().isdigit(): dc[int(p[0])] = "✓" in row
def ko(x):
    ov = [(min(b, x["e"]) - max(a, x["s"]), t) for a, b, t in K]
    ov = [o for o in ov if o[0] > 0.15]
    if not ov: return ""
    m = max(o[0] for o in ov)
    return " // ".join(t for o, t in ov if o >= m * 0.6)
ev = [(x["s"], 0, "## %.1f %s" % (x["s"], x.get("desc", "?")[:90])) for x in S]
ev += [(x["s"], 1, "%d%s %.1f %s" % (x["id"], "" if dc.get(x["id"], True) else "✗", x["s"], ko(x) or "(en) " + x["en"])) for x in L]
open("_tl.txt", "w", encoding="utf-8").write("\n".join(r for _, _, r in sorted(ev)) + "\n")
open("lines_ko.txt", "w", encoding="utf-8").write("".join(f"{x['id']}|{x['s']:.2f}|{x['e']-x['s']:.1f}s|{'✓' if dc.get(x['id'], True) else '✗'}|{x['sp']}|{x['en']}|{ko(x)}\n" for x in L))
print("_tl", len(ev), "· 자막 붙은 대사", sum(1 for x in L if ko(x)), "/", len(L))
