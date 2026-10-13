# 대사 후보 이벤트를 시간이 가장 가까운 블록 대사 목록 끝에 붙인다 (mkplan 이 블록 안 시간순 정렬)
import json, re, sys
P = json.load(open(sys.argv[1], encoding="utf-8"))
K = json.load(open("ko17.json", encoding="utf-8")); NEED = json.load(open("need.json")); EV = {e["id"]: e for e in json.load(open("subev.json"))}
for e, t in P.items(): K[e] = t; assert len(t) <= 18, t
json.dump(K, open("ko17.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
import ep17
lines = open("ep17.py", encoding="utf-8").read().split("\n")
blocks = []  # (line index, [times])
for i, ln in enumerate(lines):
    m = re.match(r'^ \("(.*?)", (\[.*\])\),\s*$', ln)
    if not m or ln.startswith(' ("R"'): continue
    ts = re.findall(r'"e(\d+)"|(?<![\w"(])(\d+)(?=[,\]])', m.group(2))
    tt = []
    for a, b in ts:
        k = ("e" + a) if a else b
        if k in NEED: tt.append(EV[NEED[k]]["s"])
    if tt: blocks.append((i, tt))
for e in P:
    s = EV[int(e)]["s"]
    i, _ = min(blocks, key=lambda b: min(abs(s - x) for x in b[1]))
    lines[i] = lines[i][:lines[i].rfind("])")] + f', "e{e}"])' + lines[i][lines[i].rfind("])") + 2:]
open("ep17.py", "w", encoding="utf-8").write("\n".join(lines))
print("붙임", len(P))
