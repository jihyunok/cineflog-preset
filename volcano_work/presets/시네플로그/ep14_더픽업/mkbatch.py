# -*- coding: utf-8 -*-
"""items.json 나레를 AI 스튜디오 한 번 생성 분량(MAX 자)씩 묶는다 → batches.json [[n0, n1, 글], ...]
아직 narr/nNNN.wav 가 없는 조각만. 사용: python mkbatch.py [MAX=1200]"""
import json, os, sys
MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
N = [q for q in json.load(open("items.json", encoding="utf-8")) if q["type"] == "N"]
B = []; cur = []
for q in N:
    if os.path.exists(f"narr/n{q['ni']:03d}.wav"):
        if cur: B.append(cur); cur = []
        continue
    if cur and sum(len(x["text"]) + 1 for x in cur) + len(q["text"]) > MAX: B.append(cur); cur = []
    cur.append(q)
if cur: B.append(cur)
out = [[b[0]["ni"], b[-1]["ni"], " ".join(x["text"] for x in b)] for b in B]
json.dump(out, open("batches.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(out), "묶음 ·", sum(len(b[2]) for b in out), "자")
