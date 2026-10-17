# -*- coding: utf-8 -*-
"""dcand.txt 를 원본 구간으로 보기. 사용: python dv.py 시작초 끝초 [all]  (기본은 ✓ 만)"""
import sys
a, b = float(sys.argv[1]), float(sys.argv[2]); ALL = "all" in sys.argv
def sec(m): x, y = m.split(":"); return int(x) * 60 + float(y)
for l in open("dcand.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("|", 4)
    if len(p) < 5: continue
    t = sec(p[1])
    if a <= t <= b and (ALL or p[3] == "✓"): print(f"{t:7.1f} {p[0]:>14} {p[2]}s {p[3][:30]:<4} {p[4][:110]}")
