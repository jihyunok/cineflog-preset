# -*- coding: utf-8 -*-
"""원본 대사 줄 표 — Speechmatics 낱말(문장부호·화자)로 줄을 나눈다(박힌 자막 줄 표가 없을 때). → lines.json [{id, s, e, en, ws, we, sp, ko}]
줄 끊기: 화자가 바뀜 · 0.7초+ 쉼 · 문장 끝 부호(.?!) · 3.15초(대사 창 최장, 1.05배속 화면 3초)를 넘기려 하면 쉼표·낱말 사이 가장 큰 틈에서.
ko 는 비어 있다 — 대본에서 우리 자막을 쓴다. 사용: python lines_sm.py"""
import json
CFG = json.load(open("ep.json", encoding="utf-8"))
W = json.load(open(CFG.get("words", "src_sm.json"), encoding="utf-8"))["words"]
lines = []; cur = []
def close():
    global cur
    if cur: lines.append(cur); cur = []
for w in W:
    if cur and (w["sp"] != cur[-1]["sp"] or w["start"] - cur[-1]["end"] > 0.7): close()
    cur.append(w)
    if any(c in w["p"] for c in ".?!"): close()
close()
out = []
for ln in lines:
    out.append({"id": len(out) + 1, "s": ln[0]["start"], "e": ln[-1]["end"], "ws": ln[0]["start"], "we": ln[-1]["end"], "sp": ln[0]["sp"],
                "en": " ".join(w["word"] + w["p"] for w in ln), "ko": None})
json.dump(out, open("lines.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
L = [x["we"] - x["ws"] for x in out]
print("줄", len(out), "· 3.15초 안", sum(l <= 3.15 for l in L), "· 넘음", sum(l > 3.15 for l in L))
