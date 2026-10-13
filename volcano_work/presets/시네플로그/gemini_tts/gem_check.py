# -*- coding: utf-8 -*-
"""자른 나레 조각마다 대본과 받아쓰기가 맞는지(앞뒤 글자) — 사용: python gem_check.py 배치.wav 시작ni 끝ni"""
import json, sys, difflib, gem_split as G
wav, n0, n1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
items = {q["ni"]: q["text"] for q in json.load(open("items.json", encoding="utf-8")) if q["type"] == "N"}
W = [(w["start"], w["end"], G.norm(w["word"])) for w in json.load(open(wav[:-4] + "_asr2.json", encoding="utf-8")).get("words", [])]
bad = 0
for i in range(n0, n1 + 1):
    a, b = json.load(open(f"narr/n{i:03d}.json", encoding="utf-8"))["src"][1:]
    got = "".join(w[2] for w in W if a <= (w[0] + w[1]) / 2 <= b); want = G.norm(items[i])
    r = difflib.SequenceMatcher(None, got, want).ratio()
    head = got[:3] == want[:3]; tail = got[-3:] == want[-3:]
    if r < 0.8 or not (head and tail): bad += 1; print("확인", i, round(r, 2), "|", got[:12], "…", got[-8:], "| 대본", want[:12], "…", want[-8:])
print("조각", n1 - n0 + 1, "의심", bad)
