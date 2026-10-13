# -*- coding: utf-8 -*-
"""대사가 2줄 미만인 나레 조각마다 근처 박힌 자막 이벤트를 더 찾아(3초 간격 지킴) addev.json {ni:[eid..]} + OCR 시트"""
import json, os, subprocess
from PIL import Image, ImageDraw
it = json.load(open("items.json", encoding="utf-8")); EV = json.load(open("subev.json"))
END = 6090
D = [q for q in it if q["type"] == "D"]
used = set(q["i"] for q in D if q["i"])
occ = [(q["s"], q["s"] + q["d"]) for q in D]
def free(s, e): return all(e + 3.0 <= a or s >= b + 3.0 for a, b in occ)
add = {}; cur = None; groups = []
for q in it:
    if q["type"] == "N": cur = {"ni": q["ni"], "rng": q["rng"], "text": q["text"], "d": []}; groups.append(cur)
    elif cur: cur["d"].append(q)
for g in groups:
    if g["ni"] > len(groups) - 9 or g["text"].startswith("오늘 소개할"): continue
    need = 3 - len(g["d"])
    if need <= 0: continue
    if g["d"]: lo = min(q["s"] for q in g["d"]) - 25; hi = max(q["s"] for q in g["d"]) + 25; c = sum(q["s"] for q in g["d"]) / len(g["d"])
    else: lo, hi = g["rng"]; c = (lo + hi) / 2
    cand = sorted([e for e in EV if lo <= e["s"] <= hi and e["e"] < END and e["id"] not in used and 0.8 <= e["e"] - e["s"] <= 3.8], key=lambda e: abs(e["s"] - c))
    for e in cand:
        if need <= 0: break
        s = e["s"] - 0.05; d = min(max(e["e"] - e["s"] + 0.15, 1.0), 3.9 if e["e"] - e["s"] + 0.15 > 2.9 else 2.9)
        if free(s, s + d): add.setdefault(g["ni"], []).append(e["id"]); used.add(e["id"]); occ.append((s, s + d)); need -= 1
prev = json.load(open("addev.json")) if os.path.exists("addev.json") else {}
known = set(json.load(open("ko13.json", encoding="utf-8")))
for k, v in add.items(): prev.setdefault(str(k), []).extend(i for i in v if i not in prev.get(str(k), []))
json.dump(prev, open("addev.json", "w"), indent=0)
ids = sorted(i for v in add.values() for i in v if str(i) not in known)
print("추가", len(ids))
evd = {e["id"]: e for e in EV}
for k in range(0, len(ids), 30):
    rows = []
    for i in ids[k:k+30]:
        e = evd[i]; t = (e["s"] + e["e"]) / 2; p = f"ocr/{i}.png"
        if not os.path.exists(p):
            subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{t:.2f}","-i","src.mp4","-frames:v","1","-vf","crop=1300:150:310:625,scale=780:90",p])
        im = Image.open(p).convert("RGB"); c = Image.new("RGB", (880, 90), "black"); c.paste(im, (100, 0))
        ImageDraw.Draw(c).text((6, 35), str(i), fill="yellow"); rows.append(c)
    S = Image.new("RGB", (880, 90 * len(rows)))
    for r, im in enumerate(rows): S.paste(im, (0, r * 90))
    S.save(f"add2_sheet_{k//30:02d}.png")
