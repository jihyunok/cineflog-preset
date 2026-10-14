# -*- coding: utf-8 -*-
"""벤치(U무비 그레이하운드 I9Jx9Co8kWs)가 이야기를 끄는 법 표 — 벤치 컷마다: 벤치 시각 · 원본 구간 · 벤치 나레(제브 판정) · 그 구간 원본 영어 대사(Speechmatics).
사용자 10-13 "벤 어떻게 이야기를 끌고가는지를 보라고 98만이나 나온영상이니까". 결과 bench_flow.md / bench_flow.json"""
import json, numpy as np
E = json.load(open("edl.json")); AU = json.load(open("audio.json"))
B = json.load(open("bench/asr_sm.json", encoding="utf-8"))["segments"]
J = {int(json.loads(l)["id"][1:]): json.loads(l)["answers"]["is_narration"] for l in open("jev_bn_out.jsonl", encoding="utf-8")}
SW = json.load(open("src_sm.json", encoding="utf-8"))["words"]
def isn(i, s):                       # 제브는 자문, 결정은 코드: 0.7+ 이거나 0.5+ 이면서 글자 8자+
    t = s["text"].replace(" ", ""); return J[i] >= 0.7 or (J[i] >= 0.5 and len(t) >= 8)
N = [dict(s, k=i) for i, s in enumerate(B) if isn(i, s)]
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
rows = []
for g in E:
    b0, b1, s0 = g["b0"], g["b1"], g["s0"]; s1 = s0 + (b1 - b0)
    nar = [n["text"] for n in N if b0 - 0.3 <= (n["start"] + n["end"]) / 2 < b1]
    au = [x for x in AU if b0 <= x["t"] < b1]
    orig = float(np.mean([x["c"] > 0.8 for x in au])) if au else 0
    en = " ".join(w["word"] for w in SW if s0 <= w["start"] < s1)
    rows.append({"b0": round(b0, 2), "b1": round(b1, 2), "s0": round(s0, 2), "s1": round(s1, 2), "narr": " ".join(nar), "orig": round(orig, 2), "en": en})
json.dump(rows, open("bench_flow.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
out = ["# 벤치 흐름표 — U무비 「그레이하운드」 (I9Jx9Co8kWs, 24:01, 98만)", "", "벤치 시각 | 원본 시각 | 길이 | 원본소리 | 벤치 나레 / 흘린 원본 대사(영어)", "---|---|---|---|---"]
for r in rows:
    out.append(f"{mm(r['b0'])}~{mm(r['b1'])} | {mm(r['s0'])}~{mm(r['s1'])} | {r['b1'] - r['b0']:.1f} | {r['orig']:.0%} | " + (f"**N** {r['narr']}" if r["narr"] else "") + (f" · D: {r['en'][:160]}" if r["en"] and r["orig"] > 0.5 else ""))
open("bench_flow.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
nt = sum(n["end"] - n["start"] for n in N)
print("벤치 컷", len(rows), "· 나레 줄", len(N), f"· 나레 {nt:.0f}초 = {nt / 1441:.0%}", "· 원본 사용 구간 합", round(sum(r['b1'] - r['b0'] for r in rows)))
