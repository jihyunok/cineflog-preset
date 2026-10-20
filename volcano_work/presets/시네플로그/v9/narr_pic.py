# -*- coding: utf-8 -*-
"""관문 ⑨ 재료: 나레 줄 밑 조각마다 (나레 영어, 그 조각 원본 그림 설명[agy shots.json]) 을 제브 나레그림_맞음.json 으로 판정 → jev_np_out.jsonl
10-13 사용자 "나래이션과 나래이션이 말하는 영상이 맞아야해 그건 가장 기본이야". 아웃트로(작품 소개)·제목 줄은 그림을 말하지 않으니 뺀다(narr_en.json 에 없는 줄).
사용: python narr_pic.py  (작업 폴더: windows.json · narr_place.json · script.py · shots.json · narr_en.json)"""
import json, os, subprocess, sys
JEV = os.path.expanduser(r"~/volcano_work/_제브")
W = json.load(open("windows.json", encoding="utf-8")); S = json.load(open("shots.json", encoding="utf-8"))
EN = json.load(open("narr_en.json", encoding="utf-8")); ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
kn = {}; ni = 0
for k, x in enumerate(ns["S"]):
    if x[0] == "N": ni += 1; kn[k] = ni
def desc(t): return next((x for x in S if x["s"] <= t < x["e"]), {}).get("desc", "")
items = []
for j, w in enumerate(W):
    n = kn.get(w.get("k"))
    if w["kind"] != "A" or n is None or str(n) not in EN: continue
    sl = (w["b"] - w["a"]) * 1.05
    items.append({"id": f"n{n:03d}_w{j}_{w['a']:.1f}", "narration": EN[str(n)], "shot": desc(w["s"] + sl / 2)})
with open("jev_np_in.jsonl", "w", encoding="utf-8") as f:
    for it in items: f.write(json.dumps(it, ensure_ascii=False) + "\n")
if os.path.exists("jev_np_out.jsonl"): os.remove("jev_np_out.jsonl")
r = subprocess.run(["py", "-3.12", rf"{JEV}\거르기.py", "--spec", rf"{JEV}\나레그림_맞음.json", "--in", "jev_np_in.jsonl", "--out", "jev_np_out.jsonl"])
A = [json.loads(l) for l in open("jev_np_out.jsonl", encoding="utf-8")]
D = {x["id"]: x for x in items}
bad = sorted((a for a in A if a["answers"]["contradicts"] >= 0.5 or a["answers"]["shows_narrated"] < 0.3), key=lambda a: -a["answers"]["contradicts"])
print("판정", len(A), "· 어긋남 0.5+ 또는 맞음 0.3 안", len(bad))
for a in bad[:60]: print(f"  {a['id']} 어긋남 {a['answers']['contradicts']:.2f} 맞음 {a['answers']['shows_narrated']:.2f} | {D[a['id']]['narration'][:60]} | {D[a['id']]['shot'][:90]}")
