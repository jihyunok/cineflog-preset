import json
IT = json.load(open("items.json", encoding="utf-8"))
D = [q for q in IT if q["type"] == "D"]
bad = 0
for i, a in enumerate(D):
    for b in D[i+1:]:
        if not (a["s"] + a["d"] + 3.0 <= b["s"] or b["s"] + b["d"] + 3.0 <= a["s"]): bad += 1
txt = json.dumps(IT, ensure_ascii=False)
print("대사", len(D), "간격 문제", bad, "18자 넘음", sum(len(q["ko"]) > 18 for q in D),
      "제목 낱말", sum(txt.count(w) for w in ["그레이하운드", "그레이 하운드", "하운드", "Greyhound", "GREYHOUND"]))
N = [q for q in IT if q["type"] == "N"]; nch = sum(len(q["text"]) for q in N)
dsec = sum(q["d"] for q in D); nmin = nch / 470
print(f"나레 {len(N)}조각 {nch}자 ≈ {nmin:.1f}분(470자/분) · 대사 {dsec/60:.1f}분 · 예상 {nmin + dsec/60:.1f}분 · 나레 비중 {nmin/(nmin+dsec/60)*100:.0f}%")
run = 0; mx = 0
for q in IT:
    if q["type"] == "N": run += 1; mx = max(mx, run)
    else: run = 0
print("나레 연속 최대", mx)
