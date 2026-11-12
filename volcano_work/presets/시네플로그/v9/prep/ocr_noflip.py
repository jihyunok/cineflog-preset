# -*- coding: utf-8 -*-
# ★사용법(11-03 ep38 에서 가져옴): 작업 폴더에 _subscan 또는 _txt 폴더를 만들어 이 파일을 넣고 그 폴더에서(subscan·textocr) / 작업 폴더에서(ocr_noflip) 돌린다. OCR 은 ../_ocr/ocr_list*.ps1(이 폴더의 ocr_list.ps1·ocr_list_en.ps1 을 _ocr 에 복사).
# 11-02 ep38: 원본 1초 OCR(text_sec.tsv)로 반전 빼기 후보 → S 번호(k) 목록. 사용: (작업 폴더에서) python _txt/ocr_noflip.py [windows.json]
# 조각(원본 s ~ s+길이) 안이나 ±0.6초에 「진짜 글자」 초가 있으면 그 줄 k 를 noflip 후보로.
import json, re, sys
W = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "windows.json", encoding="utf-8"))
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
def real(t):
    toks = re.findall(r"[A-Za-zА-Яа-я0-9]{3,}", t)
    toks = [x for x in toks if not re.fullmatch(r"[iIl1|]+", x) and len(set(x.lower())) >= 2]
    return bool(toks)
sec = {}
for r in open("_txt/text_sec.tsv", encoding="utf-8"):
    s, t = r.rstrip("\n").split("\t", 1)
    if real(t): sec[int(s)] = t
print("진짜 글자 초", len(sec))
# windows 의 줄 번호 → S 인덱스 : plan 의 windows 는 "si"(S 인덱스) 키를 가진다고 가정, 없으면 "k"
hit = {}
for w in W:
    k = w.get("si", w.get("k"))
    if k is None: continue
    L = (w["b"] - w["a"]) * w.get("rate", 1.0); a0, a1 = w["s"] - 0.6, w["s"] + L + 0.6
    for s in range(int(a0), int(a1) + 1):
        if s in sec and a0 <= s + 0.5 <= a1 + 0.5: hit.setdefault(k, []).append((s, sec[s][:40]))
for k in sorted(hit): print(k, S[k][0], str(S[k][1])[:30], hit[k][:3])
json.dump(sorted(hit), open("_txt/ocr_noflip_k.json", "w"), ensure_ascii=False)
print("후보 줄", len(hit))
