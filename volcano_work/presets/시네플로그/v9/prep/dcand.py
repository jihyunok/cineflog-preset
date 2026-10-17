# -*- coding: utf-8 -*-
"""대사 후보표 — lines.json 의 줄(과 붙어 있는 2~3줄 묶음)마다 plan_v9 와 같은 잣대(edges.snap·edge_bad, 화면 3초 = 말소리 3.15초)로
「앞뒤가 깨끗하게 잘리는가」를 미리 재서 dcand.txt 에 적는다. 대본 쓸 때 ✓ 줄만 고르면 plan 의 「말 잘림」이 처음부터 없다.
10-14 패밀리 플랜 첫 계획에서 대사 창 49곳이 말 잘림으로 걸려서. 사용: python dcand.py  →  dcand.txt (id|시각|길이|✓/✗|영어)"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import edges as EDG
CFG = json.load(open("ep.json", encoding="utf-8"))
L = json.load(open("lines.json", encoding="utf-8"))
env = EDG.Env(CFG["src"], CFG.get("words", "src_words.json"), cache=CFG.get("band", "src_band.npy"))
MAX = CFG.get("dmax", 3.0) * CFG.get("dspd", 1.05)
SW = re.compile(r"\b(shit|fuck\w*|bitch\w*|ass|asshole|damn|goddamn|piss\w*|bollocks|bastard|dick|crap)\b", re.I)
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
def test(ids):
    ln = [L[i - 1] for i in ids]
    if any(x["ws"] is None for x in ln): return None
    s0, e0 = ln[0]["ws"], ln[-1]["we"]
    if e0 - s0 > MAX: return None
    s2, e2, note = env.snap(s0, e0, MAX)
    if e2 - s2 > MAX + 1e-6: return (s2, e2, "길이")
    why = [w for w in (env.edge_bad(s2, "s", s2, e2), env.edge_bad(e2, "e", s2, e2)) if w]
    return (s2, e2, "; ".join(why))
out = []; n_ok = 0
for k in range(len(L)):
    for span in (1, 2, 3):
        ids = list(range(k + 1, k + 1 + span))
        if ids[-1] > len(L): break
        r = test(ids)
        if r is None: break
        s2, e2, why = r; en = " / ".join(L[i - 1]["en"] for i in ids)
        if SW.search(en): continue
        ok = not why; n_ok += ok
        if span > 1 and not ok: continue
        out.append(f"{ids[0] if span == 1 else ids}|{mm(s2)}|{e2 - s2:.2f}|{'✓' if ok else '✗ ' + why[:40]}|{en}")
open("dcand.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("dcand.txt", len(out), "줄 · ✓", n_ok)
