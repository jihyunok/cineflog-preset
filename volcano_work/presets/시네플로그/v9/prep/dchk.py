# -*- coding: utf-8 -*-
"""대본 D 줄 검사(03v2 10-17): 빈 줄(받아쓰기에 없는 이탈리아어 등) · 3.15초 넘음 · dcand ✓ 아님. 사용: python -X utf8 dchk.py (작업 폴더, lines_ko.txt 필요 — ko_ref.py)"""
# 대본 D 줄 검사: 빈 줄 · 3.15초 넘음 · dcand ✓ 아님 → 원본 영어·한국어 자막과 함께
import json, re
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
C = {}
for l in open("dcand.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("|", 4)
    if len(p) < 5: continue
    ids = tuple(json.loads(p[0])) if p[0].startswith("[") else (int(p[0]),)
    C[ids] = p[3]
K = {}
for r in open("lines_ko.txt", encoding="utf-8"):
    p = r.rstrip("\n").split("|")
    K[int(p[0])] = p
n = bad = 0
for k, x in enumerate(ns["S"]):
    if x[0] != "D": continue
    n += 1; ids = x[1]
    if not ids: print(f"k{k} 빈줄 「{x[2]}」"); bad += 1; continue
    ws = min(L[i]["ws"] for i in ids if L[i]["ws"] is not None); we = max(L[i]["we"] for i in ids if L[i]["we"] is not None)
    st = C.get(tuple(ids), "없음")
    if we - ws > 3.15 or "✓" not in st:
        bad += 1
        print(f"k{k} {ids} {we-ws:.2f}s {st[:30]} 「{x[2]}」 en: {' / '.join(L[i]['en'] for i in ids)}")
print("D", n, "문제", bad)
