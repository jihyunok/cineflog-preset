import json, sys
sys.stdout.reconfigure(encoding="utf-8")
exec(open("mkplan08.py", encoding="utf-8").read().split("items = []")[0])
IT = json.load(open("items.json", encoding="utf-8"))
D = [(q["s"], q["s"] + q["d"]) for q in IT if q["type"] == "D"]
used = set(q["i"] for q in IT if q["type"] == "D")
drop = [11, 13, 19, 89, 140, 150, 165, 174, 189, 204, 207, 212, 213, 225, 241, 267, 272, 287, 293, 328, 367, 412, 436, 445, 490, 530, 544, 563, 574, 583, 592, 653, 652, 679, 698, 713, 786, 797, 804, 812, 834, 838, 957, 963, 967, 1176, 994, 995, 1006, 1031, 1234, 1252, 1263, 1286, 1296, 1311, 1319, 1323, 1335, 1350, 1384, 1388, 1411, 1418, 1431]
for n in drop:
    out = []
    for m in list(range(n + 1, n + 9)) + list(range(n - 1, n - 6, -1)):
        if m in used or m < 1 or m > len(SEG): continue
        a, b = span(m); s0 = a - 0.08; e0 = min(b + 0.2, s0 + 2.9)
        if e0 - s0 < 0.6: continue
        if all(e0 + 3 <= x or s0 >= y + 3 for x, y in D):
            out.append(f"{m}:{SEG[m-1]['t'][:22]}({e0-s0:.1f})")
    print(n, " | ".join(out[:4]))
