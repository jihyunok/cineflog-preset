# -*- coding: utf-8 -*-
"""제브 나레 판정 (10-13 "제브사용해"): 나레 밑 액션 창마다 나레(영어, narr_en.json) ↔ 우리 그림 설명 / 벤치 그림 설명(shots.json, agy)을
volcano_work/_제브/나레그림_맞음.json(shows_narrated · contradicts)으로 묻는다. 벤치 그림을 기준으로 삼아 «우리만 어긋남»을 찾는다.
사용: python narr_check.py → jev_narr_in/out.jsonl, 요약·목록 출력"""
import json, os, subprocess, numpy as np
JEV = r"C:\Users\uere\volcano_work\_제브"
W = json.load(open("windows_v8.json", encoding="utf-8")); E = json.load(open("edl.json")); PL = json.load(open("narr_place.json"))
SH = json.load(open("shots.json", encoding="utf-8")); EN = json.load(open("narr_en.json", encoding="utf-8"))
def src_at(t):
    g = next((g for g in E if g["b0"] <= t < g["b1"]), E[-1]); return g["s0"] + (t - g["b0"])
def slen(w): return (w["b"] - w["a"] - w.get("hold", 0)) * (w.get("rate", 1.05) if w["kind"] == "A" else 1)
def shot(t): return next((x for x in SH if x["s"] <= t < x["e"]), SH[-1])
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
with open("jev_narr_in.jsonl", "w", encoding="utf-8") as f:
    for k, w in enumerate(W):
        if w["kind"] != "A": continue
        o, ni = max((min(w["b"], q["t"] + q["d"]) - max(w["a"], q["t"]), q["ni"]) for q in PL)
        if o < 0.3: continue
        for tag, x in (("o", w["s"] + slen(w) / 2), ("b", src_at((w["a"] + w["b"]) / 2))):
            f.write(json.dumps({"id": f"{tag}{k:04d}", "narration": EN[str(ni)], "shot": shot(x).get("desc", "")}, ensure_ascii=False) + "\n")
if os.path.exists("jev_narr_out.jsonl"): os.remove("jev_narr_out.jsonl")
subprocess.run(["py", "-3.12", rf"{JEV}\거르기.py", "--spec", rf"{JEV}\나레그림_맞음.json", "--in", "jev_narr_in.jsonl", "--out", "jev_narr_out.jsonl"])
R = {json.loads(l)["id"]: json.loads(l)["answers"] for l in open("jev_narr_out.jsonl", encoding="utf-8")}
ks = sorted({k[1:] for k in R if k[0] == "o"})
o = np.array([R["o" + k]["shows_narrated"] for k in ks]); b = np.array([R["b" + k]["shows_narrated"] for k in ks])
oc = np.array([R["o" + k]["contradicts"] for k in ks]); bc = np.array([R["b" + k]["contradicts"] for k in ks])
print(f"나레 창 {len(ks)} · 맞음 평균 우리 {o.mean():.2f}/벤치 {b.mean():.2f} · 어긋남 평균 우리 {oc.mean():.2f}/벤치 {bc.mean():.2f} · 어긋남 0.5+ 우리 {(oc >= 0.5).sum()}/벤치 {(bc >= 0.5).sum()}")
bad = [k for i, k in enumerate(ks) if oc[i] >= 0.5 and bc[i] < 0.5]
print("우리만 어긋남:", len(bad), [mm(W[int(k)]["a"]) for k in bad])
