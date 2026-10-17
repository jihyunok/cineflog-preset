# -*- coding: utf-8 -*-
"""원본 장면표: 4.5초 안짝 토막마다 시각 · agy 그림 설명 · 그 토막 영어 대사(Speechmatics) · 박힌 자막 줄 id. 사용: python sheet.py 시작초 끝초 > 출력"""
import json, sys
a0, a1 = float(sys.argv[1]), float(sys.argv[2])
S = json.load(open("shots.json", encoding="utf-8")) if __import__("os").path.exists("shots.json") else []
L = json.load(open("lines.json", encoding="utf-8"))
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
for x in S:
    if x["e"] < a0 or x["s"] > a1: continue
    ln = [l for l in L if l["ws"] is not None and x["s"] <= l["ws"] < x["e"]]
    cut = "|" if abs(x["s"] - round(x["s"], 2)) < 1e-9 and x.get("cut") is not None and (S[x["i"] - 1]["cut"] != x["cut"] if x["i"] else True) else " "
    print(f"{cut}{x['s']:7.1f} {mm(x['s']):>7} {x.get('desc', '?')}")
    for l in ln: print(f"            ▶#{l['id']} {l['ws']:.1f}-{l['we']:.1f} {l['en']}" + (f"  〔{l['ko']}〕" if l["ko"] else ""))
