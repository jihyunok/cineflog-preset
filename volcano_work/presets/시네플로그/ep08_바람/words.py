# -*- coding: utf-8 -*-
import json, glob
W = []
for k in range(11):
    d = json.load(open(f"asr/{k:02d}.json", encoding="utf-8"))
    for w in d.get("words", []): W.append((round(k*600 + w["start"], 2), round(k*600 + w["end"], 2), w["word"]))
json.dump(W, open("words.json", "w", encoding="utf-8"), ensure_ascii=False)
S = json.load(open("ko.json", encoding="utf-8"))
with open("ko_words.txt", "w", encoding="utf-8") as f:
    for i, s in enumerate(S, 1):
        ws = [w for w in W if s["s"] - 0.05 <= (w[0] + w[1]) / 2 <= s["e"] + 0.05]
        f.write(f'{i} [{s["s"]}-{s["e"]}] {s["t"]}\n   ' + " ".join(f"{w[2]}@{w[0]}-{w[1]}" for w in ws) + "\n")
print(len(W))
