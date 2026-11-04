# -*- coding: utf-8 -*-
"""시네플로그 NN 제목(견본: 다른 PC 38 노벰버 맨) — 토막 폴더 part1~4 만들기(10-21 토큰 절약: 작업자가 읽는 재료는 그 토막 구간만).
작업자가 읽는 것(srt·lines_ko·dcand·shots·bench_flow.md)은 구간(앞뒤 20초 여유)으로 자르고, 도구만 읽는 것(lines.json·scenes.txt·npy 등)은 통째로 복사.
쓰기: python _split_parts.py 경계1 경계2 경계3 끝  (원본 초, 장면 컷에 맞춤)"""
import json, os, re, shutil, sys
B = [0.0] + [float(x) for x in sys.argv[1:]]
PAD = 20
def mmss(s):
    p = s.strip().split(":"); return float(p[0]) * 60 + float(p[1]) if len(p) == 2 else float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2])
WHOLE = ["lines.json", "scenes.txt", "black_src.npy", "src_band.npy", "src_sm.json", "edl.json", "bench_flow.json", "_head.py", "_대본지시.md", "bench_asr.txt"]
for i in range(1, len(B)):
    a, b = B[i - 1], B[i]; lo, hi = a - PAD, b + PAD
    d = f"part{i}"; os.makedirs(d, exist_ok=True)
    for f in WHOLE:
        if os.path.exists(f): shutil.copy(f, d)
    ep = json.load(open("ep.json", encoding="utf-8")); ep["min_total"] = 0; ep["part"] = [a, b]
    json.dump(ep, open(f"{d}/ep.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    keep = lambda t: lo <= t <= hi
    w = lambda name, rows: open(f"{d}/{name}", "w", encoding="utf-8").write("".join(rows))
    w("srt.txt", [r for r in open("srt.txt", encoding="utf-8") if r.count("\t") >= 2 and keep(float(r.split("\t")[1]))])
    w("lines_ko.txt", [r for r in open("lines_ko.txt", encoding="utf-8") if "|" in r and keep(float(r.split("|")[1]))])
    w("dcand.txt", [r for r in open("dcand.txt", encoding="utf-8") if r.count("|") >= 3 and keep(mmss(r.split("|")[1]))])
    sh = json.load(open("shots.json", encoding="utf-8"))
    json.dump([x for x in sh if x["e"] >= lo and x["s"] <= hi], open(f"{d}/shots.json", "w", encoding="utf-8"), ensure_ascii=False)
    bf = []
    for r in open("bench_flow.md", encoding="utf-8"):
        m = re.match(r"\s*[\d:.]+~[\d:.]+\s*\|\s*([\d:.]+)~", r)
        if not m or keep(mmss(m.group(1))): bf.append(r)
    w("bench_flow.md", bf)
    print(d, f"{a:.1f}~{b:.1f}", "srt", sum(1 for _ in open(f"{d}/srt.txt", encoding="utf-8")), "dcand", sum(1 for _ in open(f"{d}/dcand.txt", encoding="utf-8")))
