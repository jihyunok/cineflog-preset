# -*- coding: utf-8 -*-
"""11-05 사용자 「~죠 이게 반복해서 들어가서 불편해」「연달아 많이 썼는데」「모든 어미는 반복해서 쓰지 말것」
나레 줄(N)을 화면 순서로 보며, 바로 앞 나레와 끝맺음 종류가 같으면 ✗ (사이에 대사가 끼어 있어도 귀에는 이어 들림).
종류: ~죠 · ~니다 · ~는데요 · 그 밖의 ~요 · 질문(?) · 연결형(, 로 끝) · 명사형/기타.
사용: 작업 폴더에서 python ending_check.py  → 문제 줄 목록 + 종류별 개수. 문제 0 이어야 녹음."""
import json, os, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
WF = "windows.json" if os.path.exists("windows.json") else "windows_dry.json"
W = json.load(open(WF, encoding="utf-8")) if os.path.exists(WF) else []
first = {}
for w in W: first.setdefault(w["k"], w["a"])
def kind(t):
    t = t.strip()
    if t.endswith("?"): return "질문"
    if t.endswith(","): return "연결형"
    u = t.rstrip(".!…\" ")
    if u.endswith("죠"): return "~죠"
    if u.endswith("는데요") or u.endswith("데요"): return "~는데요"
    if u.endswith("니다"): return "~니다"
    if u.endswith("요"): return "~요(기타)"
    return "명사형/기타"
N = [(k, x[1]) for k, x in enumerate(S) if x[0] == "N"]
bad = []
for (k0, t0), (k1, t1) in zip(N, N[1:]):
    a, b = kind(t0), kind(t1)
    if a == b:
        t = first.get(k1, 0)
        bad.append(f"  ✗ {int(t // 60)}:{t % 60:04.1f} S{k0}→S{k1} [{a}] 「{t0[-18:]}」 → 「{t1[-18:]}」")
c = collections.Counter(kind(t) for _, t in N)
print(f"어미 검사: 나레 {len(N)}줄 · 같은 끝맺음 연달아 {len(bad)}곳")
print("  " + " · ".join(f"{k} {v}({v * 100 // max(1, len(N))}%)" for k, v in c.most_common()))
print("\n".join(bad))
