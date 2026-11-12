# -*- coding: utf-8 -*-
"""11-05 52 익스팅션 사용자 「여기 넷플릭스 텍스트 공식 적용 햇어?」 → 일부만(쉼표·마침표 51, 12cps 넘음 19).
넷플릭스 자막 규칙(모든 채널 공통 — 기억 gukbbong-netflix-subtitles): 한 줄(이름표 TAG 만 두 줄 허용) · 16자(영문·공백 0.5) · 초당 12자 · 자막에 쉼표·마침표 없음.
사용: 작업 폴더에서 python nf_check.py [subs.ass] → 문제 개수와 예시. 건네기 전 0 이어야 함(빠른 자막은 대사 길이 때문이면 이유를 적고 허용)."""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
BN = chr(92) + "N"
def t2s(t): h, m, s = t.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
rows = []
for l in open(sys.argv[1] if len(sys.argv) > 1 else "subs.ass", encoding="utf-8"):
    if not l.startswith("Dialogue"): continue
    p = l.rstrip("\n").split(",", 9)
    if p[3] == "TOP": continue
    rows.append((t2s(p[1]), t2s(p[2]), p[3], re.sub(r"{[^}]*}", "", p[9])))
def ln(t): return sum(0.5 if c.isascii() else 1 for c in t)
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
two = [r for r in rows if BN in r[3] and r[2] != "TAG"]
com = [r for r in rows if re.search(r"(?<!\d),|,(?!\d)|\.", r[3].replace("…", "").replace("...", ""))]   # 11-05 숫자 2,160·말줄임은 허용
lg = [r for r in rows if ln(r[3].replace(BN, "")) > 16 and r[2] != "TAG"]
cps = [r for r in rows if r[1] > r[0] and len(r[3].replace(" ", "")) > 3 and len(r[3].replace(" ", "")) / (r[1] - r[0]) > 12]
print(f"넷플릭스 자막 검사: 자막 {len(rows)} · 두 줄 {len(two)} · 쉼표/마침표 {len(com)} · 16자 넘음 {len(lg)} · 12cps 넘음 {len(cps)}")
for name, L in (("두 줄", two), ("쉼표", com), ("16자", lg), ("빠름", cps)):
    for r in L[:8]: print(f"  ✗ {name} {mm(r[0])} {r[2]} {r[1] - r[0]:.2f}초 「{r[3]}」")
