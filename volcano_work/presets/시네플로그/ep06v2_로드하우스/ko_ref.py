# -*- coding: utf-8 -*-
"""대사 줄(lines.json)마다 원본 mkv 의 공식 한국어 자막(ko.srt, 트랙 26)에서 시각이 겹치는 줄을 붙인 참고표 → lines_ko.txt
(우리 자막은 이걸 보고 짧게 다시 쓴다 — 뜻 틀림 방지). 04v2 10-16."""
import json, re
def t(s):
    h, m, x = s.split(":"); sec, ms = x.split(","); return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
srt = []
for b in re.split(r"\n\s*\n", open("ko.srt", encoding="utf-8-sig").read().strip()):
    ls = b.strip().splitlines()
    if len(ls) >= 3 and "-->" in ls[1]:
        a, z = [t(x.strip()) for x in ls[1].split("-->")]
        srt.append((a, z, " / ".join(x.strip() for x in ls[2:])))
L = json.load(open("lines.json", encoding="utf-8"))
dc = {}
try:
    for row in open("dcand.txt", encoding="utf-8"):
        p = row.split("|")
        if p[0].strip().isdigit(): dc[int(p[0])] = "✓" if "✓" in row else "✗"
except FileNotFoundError: pass
out = []
for x in L:
    ko = [s for a, z, s in srt if a < x["e"] + 0.2 and z > x["s"] - 0.2]
    out.append(f"{x['id']}|{x['s']:.2f}|{x['e'] - x['s']:.1f}s|{dc.get(x['id'], '?')}|{x['sp']}|{x['en']}|{' // '.join(ko)}")
open("lines_ko.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("lines_ko.txt", len(out), "줄 · 공식 자막 붙은 줄", sum(1 for o in out if not o.endswith("|")))
