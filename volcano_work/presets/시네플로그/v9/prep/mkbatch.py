# -*- coding: utf-8 -*-
"""대본(script.py)의 나레 줄 → items.json [{type:N, ni, text}] + batches.json [[n0, n1, "줄\n줄…"]] (AI 스튜디오 한 번에 약 1,000자).
recv.py 가 batches.json 묶음마다 gem/bKK_n0_n1.wav 로 받는다. 이미 녹음한 글(narr/nNNN.json 의 text 가 같음)은 빼고 묶는다.
사용: python mkbatch.py [최대글자=1000]"""
import json, os, sys
# ★10-19 사용자 "tts는 호출수에따라 한도가 소진되지? 최대한 절감하는 방식으로 녹음하고 잘라" → 한 번에 2,000자(옛 1,000) ·
#   떨어진 줄(고쳐 다시 녹음할 줄)도 한 묶음에 — 묶음마다 ids(줄 번호 목록)를 4번째로 적고 gem_split·gem_check 가 그 순서로 자른다
MAXC = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
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
    if cur and sum(len(x) + 1 for _, x in cur) + len(t) > MAXC: B.append(cur); cur = []
    cur.append((i, t))
if cur: B.append(cur)
json.dump([[c[0][0], c[-1][0], "\n".join(t for _, t in c), [i for i, _ in c]] for c in B], open("batches.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", len(N), "줄 ·", sum(len(t) for t in N), "자 · 녹음할 줄", len(todo), "· 묶음", len(B), [(c[0][0], c[-1][0], sum(len(t) for _, t in c)) for c in B])
