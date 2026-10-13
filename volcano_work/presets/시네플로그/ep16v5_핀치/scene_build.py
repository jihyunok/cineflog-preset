# -*- coding: utf-8 -*-
"""원본 컷 설명(shots.json, agy) → 이웃 컷끼리 같은 장면인지 제브가 판정 → 장면 번호(scenes_jev.json) (10-13 "제브사용해").
★1판(같은장면_컷.json, 이웃 두 컷)은 차 밖↔차 안 같은 교차 편집마다 끊었다 → 2판: 앞 컷 셋(before)·뒤 컷 셋(after)을 보여 주고
같은 사건이 이어지나(continues)·새 장면이 시작되나(new_sequence) — volcano_work/_제브/같은장면_흐름.json. 경계 = new_sequence ≥ T 이고 continues < 0.5.
사용: python scene_build.py [T=0.35]  → scenes_jev.json [{i, s, e, scene}], 경계 목록 출력"""
import json, os, subprocess, sys
T = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
JEV = r"C:\Users\uere\volcano_work\_제브"
S = json.load(open("shots.json", encoding="utf-8"))
items = [{"id": f"p{S[i - 1]['i']:04d}", "before": [x.get("desc", "") for x in S[max(0, i - 3):i]], "after": [x.get("desc", "") for x in S[i:i + 3]]} for i in range(1, len(S))]
with open("jev_flow_in.jsonl", "w", encoding="utf-8") as f:
    for it in items: f.write(json.dumps(it, ensure_ascii=False) + "\n")
r = subprocess.run(["py", "-3.12", rf"{JEV}\거르기.py", "--spec", rf"{JEV}\같은장면_흐름.json", "--in", "jev_flow_in.jsonl", "--out", "jev_flow_out.jsonl"])
if r.returncode not in (0, 1): sys.exit(f"제브 실패 {r.returncode} — 원래 방식(그림 지문)으로 간다")
A = {}
for l in open("jev_flow_out.jsonl", encoding="utf-8"):
    j = json.loads(l); A[int(j["id"][1:])] = j["answers"]
sc = 0; out = []; cuts = []
for x in S:
    if out:
        a = A.get(out[-1]["i"])
        if a is None or not x.get("desc") or not S[out[-1]["i"]].get("desc"):
            pass                                            # 설명 없으면 끊지 않음
        elif a["new_sequence"] >= T and a["continues"] < 0.5:
            sc += 1; cuts.append((x["s"], round(a["continues"], 2), round(a["new_sequence"], 2), S[out[-1]["i"]]["desc"][:60], x["desc"][:60]))
    out.append({"i": x["i"], "s": x["s"], "e": x["e"], "scene": sc})
json.dump(out, open("scenes_jev.json", "w", encoding="utf-8"), indent=0)
print("컷", len(S), "· 판정", len(A), "· 장면", sc + 1)
for c in cuts: print(f"  {int(c[0]//60)}:{c[0]%60:04.1f} ({c[0]:.0f}) 이어짐{c[1]} 새장면{c[2]} | {c[3]} → {c[4]}")
