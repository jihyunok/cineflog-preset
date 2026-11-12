# -*- coding: utf-8 -*-
"""31v2 2차: 지금 windows.json 의 반전 조각 가운데 1차(_1차/windows.json — 판정자가 flipsheet 15장으로 다 본 것)와 원본 시각이 다른 것만 windows_newflip.json 으로 → prep/flipsheet.py windows_newflip.json (33v3 newflip.py 와 같은 방식)."""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
WK = r"D:\cine_work\ep31v2_잭리처"
W = json.load(open(os.path.join(WK, "windows.json"), encoding="utf-8"))
V1 = json.load(open(os.path.join(WK, "_1차", "windows.json"), encoding="utf-8"))
old = [(w["s"], w["b"] - w["a"]) for w in V1 if not w.get("noflip")]
def seen(w):
    sl = w["b"] - w["a"]
    return any(abs(s - w["s"]) < 0.3 and abs(l - sl) < 0.5 for s, l in old)
new = [w for w in W if not w.get("noflip") and not seen(w)]
json.dump(new, open(os.path.join(WK, "windows_newflip.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("반전 조각", sum(not w.get("noflip") for w in W), "· 1차와 다른 새 반전 조각", len(new))
