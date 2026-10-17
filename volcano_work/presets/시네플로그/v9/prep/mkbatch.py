# -*- coding: utf-8 -*-
"""대본(script.py)의 나레 줄 → items.json [{type:N, ni, text}] + batches.json [[n0, n1, "줄\n줄…"]] (AI 스튜디오 한 번에 약 1,000자).
recv.py 가 batches.json 묶음마다 gem/bKK_n0_n1.wav 로 받는다. 이미 녹음한 글(narr/nNNN.json 의 text 가 같음)은 빼고 묶는다.
사용: python mkbatch.py [최대글자=1000]"""
import json, os, sys
MAXC = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
N = [x[1] for x in ns["S"] if x[0] == "N"]
items = [{"type": "N", "ni": i, "text": t} for i, t in enumerate(N, 1)]
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
def done(i, t):
    p = f"narr/n{i:03d}.json"
    return os.path.exists(p) and json.load(open(p, encoding="utf-8")).get("text") == t
todo = [(i, t) for i, t in enumerate(N, 1) if not done(i, t)]
B = []; cur = []
for i, t in todo:
    if cur and (sum(len(x) + 1 for _, x in cur) + len(t) > MAXC or i != cur[-1][0] + 1): B.append(cur); cur = []
    cur.append((i, t))
if cur: B.append(cur)
json.dump([[c[0][0], c[-1][0], "\n".join(t for _, t in c)] for c in B], open("batches.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", len(N), "줄 ·", sum(len(t) for t in N), "자 · 녹음할 줄", len(todo), "· 묶음", len(B), [(c[0][0], c[-1][0], sum(len(t) for _, t in c)) for c in B])
