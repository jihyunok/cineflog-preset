# -*- coding: utf-8 -*-
import re, json, sys
src = sys.argv[1]
txt = open(src, encoding="utf-8-sig").read().replace("\r", "")
out = []
for blk in re.split(r"\n\s*\n", txt.strip()):
    L = blk.split("\n")
    if len(L) < 3: continue
    m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+) --> (\d+):(\d+):(\d+)[,.](\d+)", L[1])
    if not m: continue
    g = [int(x) for x in m.groups()]
    s = g[0]*3600+g[1]*60+g[2]+g[3]/1000; e = g[4]*3600+g[5]*60+g[6]+g[7]/1000
    t = " ".join(re.sub(r"\{[^}]*\}|<[^>]+>", "", x).strip() for x in L[2:]).strip()
    if "YTS" in t or "YIFY" in t: continue
    out.append({"s": round(s, 3), "e": round(e, 3), "t": t})
json.dump(out, open("subs_ko.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
with open("srt.txt", "w", encoding="utf-8") as f:
    for i, q in enumerate(out, 1):
        h = int(q["s"]//3600); m = int(q["s"]%3600//60); sec = q["s"]%60
        f.write(f"{i} {h}:{m:02d}:{sec:04.1f} {q['e']-q['s']:.1f} {q['t']}\n")
print(len(out))
