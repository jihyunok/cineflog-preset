# -*- coding: utf-8 -*-
import json, sys
W = json.load(open("words.json", encoding="utf-8")); S = json.load(open("ko.json", encoding="utf-8"))
for a in sys.argv[1:]:
    i = int(a); s = S[i-1]
    ws = [w for w in W if s["s"] - 0.05 <= (w[0] + w[1]) / 2 <= s["e"] + 0.05]
    print(i, f'[{s["s"]}-{s["e"]}]', s["t"][:60], "|", " ".join(f"{w[2]}@{w[0]:.1f}-{w[1]:.1f}" for w in ws)[:400])
