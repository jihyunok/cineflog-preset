# -*- coding: utf-8 -*-
"""33v3: 지금 windows.json 의 반전 조각 가운데 v2 에서 이미 본(flipsheet·textflip) 조각과 원본 시각이 다른 것만 windows_newflip.json 으로 — flipsheet.py windows_newflip.json 로 새 조각만 시트."""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
WK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = json.load(open(os.path.join(WK, "windows.json"), encoding="utf-8"))
V2 = json.load(open(r"D:\cine_work\ep33v2_콜래트럴\windows.json", encoding="utf-8"))
P1 = os.path.join(WK, "_v3", "_1차", "windows.json")   # 11-12 4차: 1차 v3 에서 본체가 이미 본 반전 조각도 뺌
V2 += json.load(open(P1, encoding="utf-8")) if os.path.exists(P1) else []
old = [(w["s"], w["b"] - w["a"]) for w in V2 if not w.get("noflip")]
def seen(w):
    sl = w["b"] - w["a"]
    return any(abs(s - w["s"]) < 0.3 and abs(l - sl) < 0.5 for s, l in old)
new = [w for w in W if not w.get("noflip") and not seen(w)]
json.dump(new, open(os.path.join(WK, "windows_newflip.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("반전 조각", sum(not w.get("noflip") for w in W), "· v2 와 다른 새 반전 조각", len(new))
