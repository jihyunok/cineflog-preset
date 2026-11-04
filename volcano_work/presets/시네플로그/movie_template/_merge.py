# -*- coding: utf-8 -*-
# 시네플로그 NN 제목(견본: 다른 PC 38 노벰버 맨) — 훅(hook_outro.py) + 토막 1~4(partN/script_part.py) + 아웃트로 → script.py · narr_en.json · emph.json
import json, os
ns = {}; exec(open("hook_outro.py", encoding="utf-8").read(), ns); HOOK, OUTRO = ns["HOOK"], ns["OUTRO"]
S = list(HOOK) + [("ZONE", "main")]
EN, EM = {}, {}
for i in range(1, 5):
    d = f"part{i}"
    src = open(f"{d}/script_part.py", encoding="utf-8").read()
    pn = {}; exec("P = [\n" + src + "\n]", pn); S += pn["P"]
    print(d, len(pn["P"]), "줄")
    if os.path.exists(f"{d}/narr_en_part.json"): EN.update(json.load(open(f"{d}/narr_en_part.json", encoding="utf-8")))
    if os.path.exists(f"{d}/emph_part.json"): EM.update(json.load(open(f"{d}/emph_part.json", encoding="utf-8")))
S += list(OUTRO)
# 이름표는 인물마다 처음 한 번만
seen = set()
for k, x in enumerate(S):
    if isinstance(x[-1], dict) and x[-1].get("tag"):
        tg = x[-1]["tag"]; nm = tg if isinstance(tg, str) else tg[0]
        if nm in seen:
            o = dict(x[-1]); o.pop("tag"); o.pop("tag_w", None); S[k] = tuple(x[:-1]) + ((o,) if o else ()); print("이름표 겹침 뺌", nm)
        seen.add(nm)
EN.update(ns["EN_HO"]); EM.update(ns["EM_HO"])
if os.path.exists("_post_merge.py"): exec(open("_post_merge.py", encoding="utf-8").read())
head = open("_head.py", encoding="utf-8").read()
open("script.py", "w", encoding="utf-8").write(head + "\n# _merge.py 가 만든다 — 시네플로그 NN 제목(견본: 다른 PC 38 노벰버 맨)(훅 + 토막 1~4 + 아웃트로)\nS = [\n" + "".join(repr(x) + ",\n" for x in S) + "]\n")
N = [x[1] for x in S if x[0] == "N"]
en = {str(i): EN[t] for i, t in enumerate(N, 1) if t in EN}
em = {"why": "10-21 다른 PC 05 — 지무비식 자막 강조(나레 번호 → [말, 감정])", "n": {str(i): EM[t] for i, t in enumerate(N, 1) if t in EM and EM[t] and EM[t][0] in t}, "dlg_yellow": []}
json.dump(en, open("narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(em, open("emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("S", len(S), "· 나레", len(N), "줄", sum(len(t) for t in N), "자 · 영어", len(en), "· 강조", len(em["n"]))
miss = [t for t in N if t not in EN]
if miss: print("영어 없는 나레", len(miss), miss[:5])
