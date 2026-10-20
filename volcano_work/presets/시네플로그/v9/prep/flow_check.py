# -*- coding: utf-8 -*-
"""흐름 검사 — 10-20 텔레그램 "5분55초에서 갑자기 다른장면이 바뀌면서 인물소개도 없고 왜 간건지도 모르겠어 … 남자친구가 왜 교도소를 들어가게 된건지 전환이 너무 빨라"
· "이 영화뿐 아니라 다음영화에서도 이런일이 일어나지 않게 확인하고 규칙을 정해."
plan_v9 뒤(windows.json 이 있으면 화면 시각도) 대본(script.py)을 화면 순서로 훑어:
 ① 장소가 바뀌는 첫 줄이 나레가 아님(대사·원음부터 시작) — 왜·어디로 갔는지 나레가 먼저 말해야 한다
 ② 주요 인물이 처음 나오는데 소개 나레가 없음(앞 나레에서 이미 이름을 말했거나 그 줄부터 8줄 안 나레에 이름이 나오면 통과) — ep.json "who_ko" {영어 이름: 한국어 이름} 에 든 인물만.
    ★시네플로그는 이름표 안 넣음(10-20 "우리는 인물 이름표는 넣지마"). ep.json "name_tag": true 인 편만 옛 검사(그 줄부터 8줄 안 이름표 tag).
장소 = 그 줄 첫 그림 구간 시작의 shots.json 설명 머리(「At Sister Husband's trailer」·「Inside the public library」…)를 ep.json "places" 낱말로 묶은 것.
  같은 건물인데 이름만 다른 자리(포니 집 = 도서관 위층 등)는 ep.json "same_place": [["forney's house", "public library"], …] 로 묶는다.
  바로 앞 줄이 나레면 그 나레가 다리라고 보고 통과 — 그 나레가 정말 「어디·왜」를 말하는지는 cold_read.py(agy, 안 본 사람 읽기)가 본다.
걸린 곳은 고치거나 ep.json "flow_ok" {"S번호 첫 글 앞 12자": "왜 괜찮은지"} 에 적는다(적힌 것은 ✓ 로 찍고 통과).
사용: python flow_check.py   → 걸린 곳 목록(남은 문제 있으면 exit 1). 훅·아웃트로 구역은 안 봄."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
CFG = json.load(open("ep.json", encoding="utf-8"))
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
SH = json.load(open("shots.json", encoding="utf-8")); L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
try: W = json.load(open("windows.json", encoding="utf-8"))
except Exception: W = []
STOP = {"at", "in", "inside", "outside", "on", "the", "a", "an", "of", "s", "other", "location", "during", "day", "night", "visible", "nobody"}
SAME = CFG.get("same_place", [])
PLACES = [(p, {w for w in re.findall(r"[a-z]+", p.lower()) if w not in STOP}) for p in CFG.get("places", [])]
def desc(t): return next((x["desc"] for x in SH if x["s"] <= t < x["e"]), "")
def place(t):
    d = desc(t); head = re.split(r"[,·]", d)[0].lower(); ws = {w for w in re.findall(r"[a-z]+", head) if w not in STOP}
    best = max(PLACES, key=lambda p: len(p[1] & ws), default=None)
    if best and best[1] & ws:
        b = best[0].lower()
        b = "walmart" if "wal-mart" in b and "wedding" not in b else b
        return next((g[0].lower() for g in SAME if b in [q.lower() for q in g]), b)
    return head.strip()
def src0(x):
    if x[0] == "N": return (x[2][0][0] if isinstance(x[2], list) else x[2])
    if x[0] == "D": ids = x[1] if isinstance(x[1], list) else [x[1]]; return L[ids[0]]["ws"]
    if x[0] == "A": return x[1]
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
scr = {}
for w in W: scr.setdefault(w["k"], w["a"])
WHO = CFG.get("who_ko", {}); seen = set(); tagged = set(); said = set(); bad = []
TAG = CFG.get("name_tag", False)   # 이름표 쓰는 채널(다른 PC 「대작」)만 true — 시네플로그는 이름표 대신 소개 나레를 잰다
KNOWN = {p.lower() for p, _ in PLACES} | {"walmart"}
items = [(k, x) for k, x in enumerate(S) if x[0] != "ZONE"]
zones = {}; z = "main"
for k, x in enumerate(S):
    if x[0] == "ZONE": z = x[1]
    zones[k] = z
pls = {k: place(src0(x) + 0.3) for k, x in items}
prev = None; seq = [k for k, _ in items if zones[k] == "main"]
for i, k in enumerate(seq):
    x = S[k]; pl = pls[k]; t = src0(x)
    when = f"화면 {mm(scr[k])}" if k in scr else f"원본 {mm(t)}"
    if pl not in KNOWN: continue                       # 「other」 같은 모르는 자리는 안 셈
    nxt = next((pls[j] for j in seq[i + 1:i + 4] if pls[j] in KNOWN), None)
    bridge = i > 0 and S[seq[i - 1]][0] == "N"
    if prev is not None and pl != prev and nxt == pl and x[0] != "N" and not bridge:   # 새 자리가 다음 줄에도 이어질 때만(잠깐 끼는 TV 화면 등은 빼고)
        what = x[2] if x[0] == "D" else "(원음)"
        bad.append((k, f"① S{k} {when} 장소 바뀜 「{prev}」→「{pl}」 첫 줄이 {x[0]} {what} — 왜·어디로 갔는지 나레 먼저"))
    if nxt == pl or prev is None: prev = pl
for k, x in items:
    if zones[k] != "main": continue
    t = src0(x); when = f"화면 {mm(scr[k])}" if k in scr else f"원본 {mm(t)}"
    op = x[-1] if isinstance(x[-1], dict) else {}
    if op.get("tag"): tagged.add(op["tag"] if isinstance(op["tag"], str) else op["tag"][0])
    if x[0] == "N": said.add(re.sub(r"\s", "", x[1]))
    d = desc(t + 0.3)
    for en, ko in WHO.items():
        if en in d and en not in seen:
            seen.add(en)
            if TAG:
                later = [y for y in S[k:k + 9] if isinstance(y[-1], dict) and y[-1].get("tag") and (y[-1]["tag"] if isinstance(y[-1]["tag"], str) else y[-1]["tag"][0]) == ko]
                if ko not in tagged and not later: bad.append((k, f"② S{k} {when} 「{ko}」({en}) 처음 나오는데 이름표 없음 — 그 인물이 혼자 크게 보이는 줄에 tag"))
            else:   # ★시네플로그(10-20 "우리는 인물 이름표는 넣지마") — 이름표 대신 소개 나레: 앞에서 이미 말했거나 그 줄부터 8줄 안 나레에 이름이 나와야
                kn = re.sub(r"\s", "", ko)
                if not any(kn in s for s in said) and not any(y[0] == "N" and kn in re.sub(r"\s", "", y[1]) for y in S[k:k + 9]):
                    bad.append((k, f"② S{k} {when} 「{ko}」({en}) 처음 나오는데 소개 나레 없음 — [처지·성격 꾸밈말] + 이름 나레를 그 줄(또는 바로 앞)에"))
OK = CFG.get("flow_ok", {})
def key(k):
    x = S[k]; t = x[1] if x[0] == "N" else x[2] if x[0] == "D" else f"A{x[1]}"
    return f"S{k} " + str(t)[:12]
left = [(k, b) for k, b in bad if key(k) not in OK]
print(f"흐름 검사: 문제 {len(bad)} · 괜찮다고 적은 것 {len(bad) - len(left)} · 남은 것 {len(left)}")
for k, b in bad: print("  ✓" if key(k) in OK else "  ✗", b, f"(괜찮음: {OK[key(k)]})" if key(k) in OK else f"  ← flow_ok 키 「{key(k)}」")
sys.exit(1 if left else 0)
