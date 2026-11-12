# 자리 없음 줄 살피기: 나레 길이 · 앞 대사 원본 끝 · 뒤 대사 원본 시작 · 그 사이 컷 설명
import json, sys, ast, wave
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
SH = json.load(open("shots.json", encoding="utf-8"))
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
ni = {}; n = 0
for k, x in enumerate(S):
    if x[0] == "N": n += 1; ni[k] = n
for k in map(int, sys.argv[1:]):
    x = S[k]; w = f"narr/n{ni[k]:03d}.wav"
    with wave.open(w) as f: d = f.getnframes() / f.getframerate()
    pe = max((L[i]["we"] or 0) for j in range(k - 1, -1, -1) if S[j][0] == "D" for i in S[j][1]) if any(S[j][0] == "D" for j in range(k)) else 0
    pj = next(j for j in range(k - 1, -1, -1) if S[j][0] == "D"); pe = max(L[i]["we"] for i in S[pj][1] if L[i]["we"])
    nj = next(j for j in range(k + 1, len(S)) if S[j][0] == "D"); ns_ = min(L[i]["ws"] for i in S[nj][1] if L[i]["ws"] is not None)
    print(f"줄{k} n{ni[k]:03d} {d:.2f}초 「{x[1]}」 구간 {x[2]} · 앞 대사 줄{pj} 원본 끝 {pe:.1f}({mm(pe)}) · 뒤 대사 줄{nj} 원본 시작 {ns_:.1f}({mm(ns_)})")
    for s in SH:
        if pe - 6 <= s["s"] <= ns_ + 2: print(f"    {s['s']:.1f}-{s['e']:.1f} {s.get('desc','')[:120]}")
