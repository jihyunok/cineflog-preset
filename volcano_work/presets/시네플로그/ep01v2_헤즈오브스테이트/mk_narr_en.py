# -*- coding: utf-8 -*-
"""script.py 의 N 순서대로 narr_en.json {"번호": 영어} — 제목 줄·아웃트로 줄은 뺀다. 영어는 narr_en_src.py 의 EN(한국어 → 영어)."""
import json
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); en = {}; exec(open("narr_en_src.py", encoding="utf-8").read(), en)
z = "main"; i = 0; out = {}; miss = []
for x in ns["S"]:
    if x[0] == "ZONE": z = x[1]; continue
    if x[0] != "N": continue
    i += 1
    if z == "outro" or "결말까지 바로 시작" in x[1]: continue
    if x[1] in en["EN"]: out[str(i)] = en["EN"][x[1]]
    else: miss.append((i, x[1]))
json.dump(out, open("narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("narr_en", len(out), "· 번역 없음", miss)
