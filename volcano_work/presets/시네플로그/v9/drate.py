# -*- coding: utf-8 -*-
"""대사 창(kind D)도 1.05배속 — 소리도 같이(atempo, 입 모양 맞음). (10-14 17 그레이하운드 Apple IPE 영상 소유권 주장 뒤 사용자 "그렇게해줘")
까닭: 대사 창은 반전·배속 없이 원본 그대로였다 → 17편은 대사 창이 화면의 63%(핀치 31%)라 걸린 구간 10곳의 72% 가 대사 창.
방법: 1.05배로 틀면 원본이 창 길이의 5% 더 필요하다 → 그만큼을 창 앞뒤의 '조용한 틈'으로만 늘린다(낱말이 잘리면 안 됨, edges 잣대).
      틈이 모자란 창은 배속을 그만큼 낮춘다(1.0~1.05). 원본 3초 간격(gate ⑥)도 지킨다(이웃과 남는 간격의 절반까지만).
결과: windows.json 의 D 창에 pre(원본 시작을 앞당긴 초)·rate 를 적는다 → build_v9 cut 이 그대로 쓴다. gate ⑥⑦⑧ 도 pre·rate 로 잰다.
사용: python drate.py [windows.json]   (작업 폴더에서, ep.json 필요)
★10-14 v11 부터 안 쓴다: v10 도 소유권 주장 그대로 → plan_v9 가 대사 창을 처음부터 3초 안·1.05배(rate, pre 0)로 짠다. 이걸 돌리면 그 rate 를 지우고 다시 늘리므로 돌리지 말 것."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import edges as EDG
SPD, GAP, BUF = 1.05, 3.0, 0.05
FN = sys.argv[1] if len(sys.argv) > 1 else "windows.json"
CFG = json.load(open("ep.json", encoding="utf-8"))
WN = json.load(open(FN, encoding="utf-8"))
env = EDG.Env(CFG["src"], CFG.get("words", "src_words.json"), cache=CFG.get("band", "src_band.npy"))
db = env.db

def span(w):
    if w["kind"] == "A": r = w.get("rate", SPD)
    else: r = w.get("rate", 1.0)
    s0 = w["s"] - w.get("pre", 0.0); return s0, s0 + (w["b"] - w["a"]) * r

def quiet_run(t, direction, th, limit=1.5):
    """t 에서 direction(-1 앞 / +1 뒤)으로 조용한(th 아래) 칸이 이어지는 초"""
    k = env.k(t); n = 0
    while n * EDG.HOP < limit:
        j = k + direction * n if direction > 0 else k - 1 - n
        if j < 0 or j >= len(db) or db[j] >= th: break
        n += 1
    return n * EDG.HOP

for w in WN:                                   # 다시 돌려도 같게: 앞서 적은 값 지우고 시작
    if w["kind"] == "D": w.pop("pre", None); w.pop("rate", None)

stat = {"full": 0, "part": 0, "none": 0}; back = 0
for i, w in enumerate(WN):
    if w["kind"] != "D": continue
    L = w["b"] - w["a"]; s, e = w["s"], w["s"] + L; need = (SPD - 1) * L
    th = env.thr(s, e)
    qb = quiet_run(s, -1, th) - BUF; qa = quiet_run(e, +1, th) - BUF
    # 낱말 시각으로도 막는다(앞 줄 끝 낱말·다음 줄 첫 낱말)
    pe = max((x[1] for x in env.W if x[1] <= s + 0.02 and x[0] < s), default=-9e9)
    ns = min((x[0] for x in env.W if x[0] >= e - 0.02 and x[1] > e), default=9e9)
    wb, wa = s - pe - 0.1, ns - e - 0.1
    qb = min(qb, wb); qa = min(qa, wa)
    # 배경음(수중음파 핑·엔진)이 이어져 조용한 틈이 없으면: 낱말 없는 곳으로 0.35초까지(새 가장자리는 아래 edge_bad 로 다시 잰다)
    qb2 = min(wb, max(qb, 0.35)); qa2 = min(wa, max(qa, 0.35))
    # 원본 3초 간격: 같은 구역 이웃 창과 남는 간격의 절반까지
    z = w.get("z", "main"); others = [span(x) for j, x in enumerate(WN) if j != i and x.get("z", "main") == z]
    gb = min((s - y1 - GAP for y0, y1 in others if y1 <= s + 0.01), default=9e9)
    ga = min((y0 - e - GAP for y0, y1 in others if y0 >= e - 0.01), default=9e9)
    def alloc(qb, qa):
        ab = max(0.0, min(qb, gb / 2)); aa = max(0.0, min(qa, ga / 2))
        pre = min(ab, need / 2); post = min(aa, need - pre)
        if pre + post < need: pre = min(ab, need - post)
        return pre, post
    def bad(pre, post):           # 새 가장자리에서 말이 잘리나
        return (pre > 0 and env.edge_bad(s - pre, "s", s - pre, e + post)), (post > 0 and env.edge_bad(e + post, "e", s - pre, e + post))
    pre, post = alloc(qb2, qa2); bs, be = bad(pre, post)
    if bs or be:                  # 넓힌 쪽에서 걸리면 조용한 틈만으로
        pre1, post1 = alloc(qb if bs else qb2, qa if be else qa2); pre, post = pre1, post1; bs, be = bad(pre, post)
    if bs: pre = 0.0; back += 1
    if be: post = 0.0; back += 1
    r = 1 + (pre + post) / L
    if r > 1.0005:
        w["pre"] = round(pre, 3); w["rate"] = round(r, 4)
    stat["full" if r >= SPD - 0.002 else ("part" if r > 1.0005 else "none")] += 1

json.dump(WN, open(FN, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
rs = [w.get("rate", 1.0) for w in WN if w["kind"] == "D"]
print(f"대사 창 {len(rs)} · 1.05배 {stat['full']} · 일부 {stat['part']} · 그대로 1.0 {stat['none']} · 평균 {np.mean(rs):.4f} · 가장자리 때문에 물린 쪽 {back}")
