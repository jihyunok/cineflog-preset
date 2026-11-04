# -*- coding: utf-8 -*-
# srt.txt 에 빠진 줄만 다시 번역해 채운다
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
W = "D:/cine_work/ep22_하비의마지막로맨스"
L0 = json.load(open(f"{W}/lines.json", encoding="utf-8"))
old = {int(l.split("\t")[0]): l for l in open(f"{W}/srt.txt", encoding="utf-8")}
miss = [x for x in L0 if x["id"] not in old]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mk_srt.py"), encoding="utf-8").read()
ns = {"__name__": "lib"}
exec(src.split("parts = ")[0], ns)        # job·CTX 만 불러온다
import concurrent.futures as cf
parts = [miss[i:i + 125] for i in range(0, len(miss), 125)]
res = {}
with cf.ThreadPoolExecutor(2) as ex:
    for got in ex.map(lambda a: ns["job"](*a), enumerate(parts)): res.update(got)
for x in miss:
    if x["id"] in res: old[x["id"]] = "%d\t%.1f\t%.1f\t%s\n" % (x["id"], x["s"], x["e"], res[x["id"]])
with open(f"{W}/srt.txt", "w", encoding="utf-8") as f:
    for k in sorted(old): f.write(old[k])
print("done", len(res), "/", len(miss))
