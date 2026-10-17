# -*- coding: utf-8 -*-
"""캡컷 드래프트 뒷손질: 나레 자막이 대사 트랙으로 잘못 갈린 것 되돌리기(★10-14 끝 음원 15초 검은 화면은 뺌 — 사용자 "영상 끝나고 10초넘게 시커먼화면이 나오는거확인하고 지워"). 사용: python capfix.py 드래프트폴더 자막.ass"""
import json, glob, sys, os
D, A = sys.argv[1], sys.argv[2]
def _t(x):
    h, m, c = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(c)
# 10-13: 글자만 같으면 대사 「제프」「핀치」도 나레로 옮겼다 → 글자 + 시작 시각(0.1초 안)이 같은 줄만
import re   # ★10-16 지무비식 자막: 나레 꼴 NP(일반)·NE(강조)도 나레, 꾸밈 기호는 빼고 글자로 맞춘다
NT = [(re.sub(r"\{[^}]*\}", "", f[9]), _t(f[1])) for f in (l.rstrip("\n").split(",", 9) for l in open(A, encoding="utf-8") if l.startswith("Dialogue")) if f[3] in ("N", "NP", "NE")]
def is_n(s, M): t = json.loads(M[s["material_id"]]["content"])["text"]; a = s["target_timerange"]["start"] / 1e6; return any(t == x and abs(a - y) < 0.1 for x, y in NT)
for p in [f"{D}/draft_content.json"] + glob.glob(f"{D}/Timelines/*/draft_content.json"):
    d = json.load(open(p, encoding="utf-8")); M = {m["id"]: m for m in d["materials"]["texts"]}
    T = {t.get("name"): t for t in d["tracks"] if t["type"] in ("text", "audio")}
    n, dd = T["나레이션 자막"], T["대사 자막"]
    mv = [s for s in dd["segments"] if is_n(s, M)]
    dd["segments"] = [s for s in dd["segments"] if s not in mv]; n["segments"] = sorted(n["segments"] + mv, key=lambda s: s["target_timerange"]["start"])
    for t in d["tracks"]:
        if t.get("name") == "로고":
            for s in t["segments"]: s["target_timerange"]["duration"] = d["duration"] - s["target_timerange"]["start"]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    print(os.path.basename(os.path.dirname(p)), "옮김", len(mv), "·", round(d["duration"] / 6e7, 2), "분")
