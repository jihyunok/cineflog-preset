# -*- coding: utf-8 -*-
"""등장인물 이름 한 번 더 확인 (11-03 사용자 「이름 안바뀌게 잘 확인해」「영상 속 등장인물 이름 다시 한번 확인하는 규칙 넣어」) — 영화·드라마 공통.
38 노벰버 맨: 나레·이름표는 「데버로」「메이슨」인데 대사 자막에 실제 이름 「피터」 6곳·「데이빗」 2곳이 섞여 다른 사람처럼 보였다.
검사: script.py 의 나레(N)·대사 자막(D)·이름표(tag)를 모아
 ① 이름표 이름과 한 글자만 다른 표기(헨리/핸리·페데로프/페도로프·새라/세라) — 표기 흔들림
 ② ep.json "name_alias": {"데버로": ["피터"], "메이슨": ["데이빗"]} 의 다른 이름(성·이름·별명·가명)이 혼자 쓰인 곳 — 「피터 데버로」처럼 같이 쓰면 괜찮음
 ③ 인물마다 쓰인 표기 목록(눈으로 한 번 더)
사용: (작업 폴더에서) python name_check.py → 걸린 줄 목록, 걸리면 exit 1. 녹음 전(편집자 통독 뒤)·넘기기 전에 돌린다."""
import difflib, json, os, re, sys
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
CFG = json.load(open("ep.json", encoding="utf-8")) if os.path.exists("ep.json") else {}
ALIAS = CFG.get("name_alias", {})
NAME_OK = CFG.get("name_ok", [])  # 11-03 ep41: 정체 고백처럼 다른 이름을 일부러 쓰는 줄(글 일부) — ② 건너뜀
rows = []
for k, x in enumerate(S):
    if x[0] == "N": rows.append((k, "N", x[1]))
    elif x[0] == "D": rows.append((k, "D", x[2]))
    d = x[-1] if isinstance(x[-1], dict) else {}
    if d.get("tag"): t = d["tag"]; rows.append((k, "T", t if isinstance(t, str) else t[0]))
canon = []
for k, kind, t in rows:
    if kind == "T":
        for w in t.split():
            if len(w) >= 2 and w not in canon: canon.append(w)
for c in ALIAS:
    if c not in canon: canon.append(c)
for c in CFG.get("who_ko", {}).values():   # 시네플로그는 이름표가 없어 ep.json who_ko 를 기준 표기로 쓴다
    if c not in canon: canon.append(c)
bad = []
toks = {}
for k, kind, t in rows:
    for w in re.findall(r"[가-힣]{2,}", t):
        toks.setdefault(w, []).append((k, kind, t))
# ① 한 글자 다른 표기
for w, occ in toks.items():
    for c in canon:
        base = w[:len(c)]
        if base != c and len(c) >= 2 and len(base) == len(c) and difflib.SequenceMatcher(None, base, c).ratio() >= 0.66 \
                and sum(a != b for a, b in zip(base, c)) == 1 and not any(base == cc for cc in canon) \
                and not (base[-1] != c[-1] and base[-1] in "은는이가을를의에도로와과"):   # 11-04 끝 글자가 조사면 다른 사람 이름이 아니다
            for k, kind, t in occ[:3]: bad.append(f"① 표기 흔들림 「{base}」 ↔ 「{c}」 · S{k} {kind} {t}")
# ② 다른 이름 혼자
for c, al in ALIAS.items():
    for a in al:
        for k, kind, t in rows:
            if any(o in t for o in NAME_OK): continue
            for m in re.finditer(re.escape(a), t):
                near = t[max(0, m.start() - 6): m.end() + 6]
                if c not in near: bad.append(f"② 다른 이름 「{a}」(= {c}) · S{k} {kind} {t}")
# ③ 인물별 표기
print("기준 인물:", " · ".join(canon))
for c in canon:
    n = sum(len(v) for w, v in toks.items() if w.startswith(c))
    print(f"  {c}: {n}번")
for b in dict.fromkeys(bad): print("✗", b)
print("이름 검사:", "문제 0" if not bad else f"문제 {len(dict.fromkeys(bad))}")
sys.exit(1 if bad else 0)
