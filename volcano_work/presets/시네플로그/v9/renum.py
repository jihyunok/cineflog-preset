# -*- coding: utf-8 -*-
"""(작업 폴더에서 실행) 대본을 고친 뒤 나레 번호 다시 매기기 — 글이 같은 옛 녹음은 새 번호로 복사(옛 narr 는 narr_old_N 으로 옮김). 사용: python renum.py 옛폴더1 옛폴더2 ..."""
import json, os, re, shutil, sys
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
k = 1
while os.path.exists(f"narr_old_{k}"): k += 1
os.rename("narr", f"narr_old_{k}")
old = {}
for d in [f"narr_old_{k}"] + sys.argv[1:]:
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            old.setdefault(json.load(open(f"{d}/{f}", encoding="utf-8"))["text"], f"{d}/{f[:-5]}")
os.makedirs("narr")
new = [x[1] for x in S if x[0] == "N"]; m = {}; miss = []
for i, t in enumerate(new, 1):
    if t in old:
        for ext in (".wav", ".json"): shutil.copy2(old[t] + ext, f"narr/n{i:03d}{ext}")
        m[f"n{i:03d}"] = old[t]
    else: miss.append((i, t))
json.dump({"from": m, "miss": miss}, open("narr_renum_last.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", len(new), "· 재사용", len(m), "· 새로", len(miss), "· 새 글자", sum(len(re.sub(r"\s", "", t)) for _, t in miss))
