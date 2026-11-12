# -*- coding: utf-8 -*-
"""11-07 60 익스트랙션: 로컬 받아쓰기(whisper)가 액션 구간 대사를 통째로 놓침(결말 21분 대사 줄 0개, 한국어 자막은 56줄) → 나레 76%.
영어 자막 파일(en.srt — mkv 영어 자막 트랙)의 대사 줄 중 lines.json 의 어느 줄과도 안 겹치는 것을 새 줄(id 20001~)로 붙인다.
lines.json · dcand.txt · lines_ko.txt 에 시각 순으로 끼워 넣음(✓ = 3.15초 안 · 피할 구간 밖). 기존 id 는 그대로 — dcand.py 다시 돌리지 말 것.
[소리 표시]만 있는 줄은 뺌. 한국어 뜻은 ko.srt(공식 자막)에서 겹치는 줄.
사용: 작업 폴더에서 split_long.py 다음, 대본 쓰기 전에 python fill_en_srt.py [끝초=ep.json 크레딧 avoid 시작]
영어 자막이 없는 편(박힌 자막 OCR 편, 61 그레이 맨): python fill_en_srt.py --ko [끝초] → ko.srt 줄 시각으로 채움(en 칸에도 한국어)."""
import json, re, sys, shutil
def t2s(x):
    h, m, s = x.split(":"); s, ms = s.split(","); return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
def cues(fn):
    out = []
    for b in re.split(r"\n\s*\n", open(fn, encoding="utf-8-sig").read().replace("\r", "").strip()):
        L = b.split("\n")
        if len(L) < 3 or "-->" not in L[1]: continue
        a, z = [t2s(x.strip()) for x in L[1].split("-->")]
        out.append((a, z, " / ".join(re.sub(r"<[^>]+>|\{[^}]*\}", "", x).replace("‪", "").replace("‬", "").strip() for x in L[2:] if x.strip())))
    return out
USE_KO = "--ko" in sys.argv
if USE_KO: sys.argv.remove("--ko")
KO = cues("ko.srt"); EN = KO if USE_KO else cues("en.srt")
L = json.load(open("lines.json", encoding="utf-8")); ep = json.load(open("ep.json", encoding="utf-8")); av = ep.get("avoid", [])
END = float(sys.argv[1]) if len(sys.argv) > 1 else max([a for a, b in av if b >= ep.get("srclen", 1e9) - 1] or [1e9])
for f in ("lines.json", "dcand.txt", "lines_ko.txt"): shutil.copy(f, f + ".pre_en")
inav = lambda a, z: any(p < z and q > a for p, q in av)
new = []; nid = max([20000] + [x["id"] for x in L if x["id"] >= 20000]) + 1
for a, z, t in EN:
    if a >= END: continue
    clean = re.sub(r"\[[^\]]*\]", "", t).replace("-", "").strip(" /")
    if not re.search(r"[A-Za-z]{2}" if not USE_KO else r"[가-힣]{2}", clean) or any(x["s"] < z and x["e"] > a for x in L): continue
    ko = " // ".join(k for p, q, k in KO if p < z - 0.1 and q > a + 0.1)
    new.append({"id": nid, "s": round(a, 2), "e": round(z, 2), "ws": round(a, 2), "we": round(z, 2), "sp": "S1", "en": clean, "ko": ko or None, "src": "en.srt"}); nid += 1
json.dump(L + new, open("lines.json", "w", encoding="utf-8"), ensure_ascii=False)
mm = lambda s: f"{int(s // 60)}:{s % 60:04.1f}"
ok = lambda x: x["e"] - x["s"] <= 3.15 and not inav(x["s"], x["e"])
def key(r):
    try: p = r.split("|")[1].split(":"); return float(p[0]) * 60 + float(p[1])
    except Exception: return 0
rows = [(key(r), r) for r in open("dcand.txt", encoding="utf-8").read().splitlines()]
rows += [(x["s"], f"{x['id']}|{mm(x['s'])}|{x['e'] - x['s']:.2f}|{'✓' if ok(x) else '✗ 피할 구간 또는 3.15초 넘음'}|{x['en']}") for x in new]
open("dcand.txt", "w", encoding="utf-8").write("\n".join(r for _, r in sorted(rows, key=lambda r: r[0])) + "\n")
lr = [(float(r.split("|")[1]), r) for r in open("lines_ko.txt", encoding="utf-8").read().splitlines() if r.count("|") >= 5]
lr += [(x["s"], f"{x['id']}|{x['s']}|{x['e'] - x['s']:.1f}s|{'✓' if ok(x) else '✗'}|S1|{x['en']}|{x['ko'] or ''}") for x in new]
open("lines_ko.txt", "w", encoding="utf-8").write("\n".join(r for _, r in sorted(lr, key=lambda r: r[0])) + "\n")
print("영어 자막으로 채운 새 대사 줄", len(new), "· ✓", sum(1 for x in new if ok(x)))
