# -*- coding: utf-8 -*-
"""드루와 03 — 로컬 whisper 받아쓰기는 문장을 길게 이어 붙여 3.15초 넘는 줄이 1,043개(112분) → 대사 후보에서 빠짐.
긴 줄을 낱말 시각으로 3초 안 조각으로 쪼개 새 줄(id 10001~)로 lines.json 끝에 붙이고, dcand 와 같은 잣대로 재서
dcand.txt·lines_ko.txt 에 시각 순으로 끼워 넣는다. 기존 id 는 그대로(작업자가 쓴 D 가 깨지지 않게).
⚠ 이 뒤로 dcand.py 를 다시 돌리면 안 된다(dcand.py 는 id = 순번이라고 가정). 사용: python split_long.py"""
import json, os, re, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import edges as EDG
CFG = json.load(open("ep.json", encoding="utf-8"))
for f in ("lines.json", "dcand.txt", "lines_ko.txt"):
    if not os.path.exists(f + ".orig"): shutil.copy(f, f + ".orig")
L = json.load(open("lines.json.orig", encoding="utf-8"))
W = json.load(open(CFG["words"], encoding="utf-8"))["words"]
env = EDG.Env(CFG["src"], CFG["words"], cache=CFG.get("band", "src_band.npy"))
MAX = CFG.get("dmax", 3.0) * CFG.get("dspd", 1.05); CUT = 2.9
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
def split(ws):
    if ws[-1]["end"] - ws[0]["start"] <= CUT or len(ws) < 2: return [ws]
    best = None
    for i in range(1, len(ws)):
        a, b = ws[:i], ws[i:]
        if a[-1]["end"] - a[0]["start"] < 0.5 or b[-1]["end"] - b[0]["start"] < 0.5: continue
        gap = ws[i]["start"] - ws[i - 1]["end"]
        sc = gap + (0.4 if any(c in ws[i - 1].get("p", "") for c in ",.?!") else 0) - 0.05 * abs((a[-1]["end"] - a[0]["start"]) - (b[-1]["end"] - b[0]["start"]))
        if best is None or sc > best[0]: best = (sc, i)
    if best is None: return [ws]
    return split(ws[:best[1]]) + split(ws[best[1]:])
new = []; nid = 10001
for x in L:
    if x["we"] - x["ws"] <= MAX: continue
    ws = [w for w in W if w["start"] >= x["ws"] - 0.01 and w["end"] <= x["we"] + 0.01 and w["sp"] == x["sp"]]
    for p in split(ws):
        if not p or p[-1]["end"] - p[0]["start"] > MAX: continue
        new.append({"id": nid, "s": p[0]["start"], "e": p[-1]["end"], "ws": p[0]["start"], "we": p[-1]["end"], "sp": x["sp"],
                    "en": " ".join(w["word"] + w.get("p", "") for w in p), "ko": None, "from": x["id"]}); nid += 1
json.dump(L + new, open("lines.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
rows = []; ok = 0
for k, x in enumerate(new):
    for span in (1, 2):
        grp = new[k:k + span]
        if len(grp) < span or grp[-1]["from"] != grp[0]["from"]: break
        s0, e0 = grp[0]["ws"], grp[-1]["we"]
        if e0 - s0 > MAX: break
        s2, e2, _ = env.snap(s0, e0, MAX)
        if e2 - s2 > MAX + 1e-6: why = "길이"
        else: why = "; ".join(w for w in (env.edge_bad(s2, "s", s2, e2), env.edge_bad(e2, "e", s2, e2)) if w)
        if span > 1 and why: continue
        ok += not why; ids = grp[0]["id"] if span == 1 else [g["id"] for g in grp]
        rows.append((s2, f"{ids}|{mm(s2)}|{e2 - s2:.2f}|{'✓' if not why else '✗ ' + why[:40]}|" + " / ".join(g["en"] for g in grp)))
def tsec(r):
    t = r.split("|")[1]; m, s = t.split(":"); return int(m) * 60 + float(s)
old = [r.rstrip("\n") for r in open("dcand.txt.orig", encoding="utf-8") if r.count("|") >= 3]
allr = sorted([(tsec(r), r) for r in old] + rows, key=lambda z: z[0])
open("dcand.txt", "w", encoding="utf-8").write("\n".join(r for _, r in allr) + "\n")
ko = [r.rstrip("\n") for r in open("lines_ko.txt.orig", encoding="utf-8") if "|" in r]
ko += [f"{x['id']}|{x['ws']:.2f}|{x['we'] - x['ws']:.1f}s|?|{x['sp']}|{x['en']}|{x['en']}" for x in new]
ko.sort(key=lambda r: float(r.split("|")[1]))
open("lines_ko.txt", "w", encoding="utf-8").write("\n".join(ko) + "\n")
print("긴 줄 쪼갠 새 줄", len(new), "· 새 후보", len(rows), "· ✓", ok, f"· ✓ 길이 {sum(float(r.split('|')[2]) for _, r in rows if '|✓|' in r) / 60:.1f}분")
