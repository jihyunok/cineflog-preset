# -*- coding: utf-8 -*-
"""「영화 안 본 사람」 읽기 검사 — 대본(script.py)을 화면 순서대로 글로 풀어 agy 에게 처음 보는 시청자로 읽힌다.
10-20 텔레그램 "5분55초에서 갑자기 다른장면이 바뀌면서 인물소개도 없고 왜 간건지도 모르겠어 … 남자친구가 왜 교도소를 들어가게 된건지 전환이 너무 빨라 이해도가 떨어져"
· "이 영화뿐 아니라 다음영화에서도 이런일이 일어나지 않게 확인하고 규칙을 정해."
flow_check.py(장소 바뀜·이름표 — 기계 검사)가 못 보는 「왜」를 본다:
 장소 = 다른 곳으로 넘어갔는데 어디·왜 갔는지 그 줄(또는 바로 앞 줄)에서 안 들림
 인물 = 중요한 인물이 처음 나오는데 누구인지(이름·관계) 안 들림
 원인 = 체포·죽음·이별·이사·사고·결혼 같은 큰 사건의 이유가 안 들림(대사로 나왔는데 그 대사를 뺐으면 나레가 말해야 함)
 뜬금 = 앞뒤 이어짐 없이 갑자기 나온 말
 장면 = 죽음·사고·체포·고백·이별 같은 큰 사건을 나레 한 줄로만 말하고 그 장면(원음 대사·소리 장면)이 화면에 없음
 감정 = 인물이 마음과 반대로 말하거나(거절·거짓말·이별) 크게 흔들리는데 왜 그러는지(속마음) 안 들림
 (10-20 텔레그램 "포니 누나가 사망한 영상도 없고 포니를 밀어낼때 노블리의 감정을 표현하는곳도 없어. 시청자가 갑자기? 이런 느낌이 들거야." · "이영화처럼 실수하지 않게 규칙 정해.")
녹음 전에 돌리고, 나온 것은 전부 고치거나 ep.json "cold_ok" {"S번호 첫 글 앞 12자": "왜 괜찮은지"} 에 적는다.
★agy 는 매번 조금씩 다르게 짚고 영화 내용을 짐작해 틀린 fix 를 내기도 한다(03 v3: 「까막눈」·「성금을 노리고」 같은 지어낸 이유) — 목록은 판정이 아니라 후보다.
  줄마다 원본 대사(srt)·그림으로 사실을 확인하고 고칠지 정한다. fix 문장을 그대로 쓰지 않는다.
사용: python cold_read.py [--title 영화제목]   → cold_read.json · 화면 출력"""
import json, os, re, subprocess, sys, tempfile
sys.stdout.reconfigure(encoding="utf-8")
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
CFG = json.load(open("ep.json", encoding="utf-8"))
TITLE = sys.argv[sys.argv.index("--title") + 1] if "--title" in sys.argv else CFG.get("title_ko", CFG.get("title", ""))
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
SH = json.load(open("shots.json", encoding="utf-8")); L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
def desc(t): return next((x["desc"] for x in SH if x["s"] <= t < x["e"]), "")
def src0(x):
    if x[0] == "N": return (x[2][0][0] if isinstance(x[2], list) else x[2])
    if x[0] == "D": ids = x[1] if isinstance(x[1], list) else [x[1]]; return L[ids[0]]["ws"]
    if x[0] == "A": return x[1]
def short(d): return re.sub(r"\s+", " ", d)[:110]
rows = []; zone = "main"
for k, x in enumerate(S):
    if x[0] == "ZONE": zone = x[1]; rows.append((k, f"──── {'훅(예고 — 본편 장면을 미리 보여 주는 곳)' if zone == 'hook' else '아웃트로' if zone == 'outro' else '본편'} ────")); continue
    op = x[-1] if isinstance(x[-1], dict) else {}
    tg = op.get("tag"); tg = (" [화면 이름표: " + (tg if isinstance(tg, str) else " · ".join(tg)) + "]") if tg else ""
    d = short(desc(src0(x) + 0.3))
    if x[0] == "N": rows.append((k, f"S{k} [나레] {x[1]}{tg}  〔화면: {d}〕"))
    elif x[0] == "D": rows.append((k, f"S{k} [대사 자막] {x[2].replace(' / ', ' ')}{tg}  〔화면: {d}〕"))
    elif x[0] == "A": rows.append((k, f"S{k} [말 없는 원래 소리 장면 {x[2] - x[1]:.0f}초]  〔화면: {d}〕"))
W = os.path.join(tempfile.gettempdir(), "agy_cold"); os.makedirs(W, exist_ok=True)
SCH = os.path.join(W, "s.json")
json.dump({"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "S": {"type": "integer"}, "kind": {"type": "string"}, "why": {"type": "string"}, "fix": {"type": "string"}},
    "required": ["S", "kind", "why", "fix"]}}}, "required": ["items"]}, open(SCH, "w", encoding="utf-8"))
RULE = ("도구·명령어 쓰지 말고 글로만 답해. 너는 영화 「" + TITLE + "」를 한 번도 안 본 유튜브 시청자다. 아래는 이 영화를 소개하는 리뷰 영상을 화면 순서대로 적은 것이다. "
        "들리는 것은 [나레]와 [대사 자막]뿐이고, 〔화면〕은 눈에 보이는 그림이다(화면 설명의 영어 이름은 시청자가 모른다 — 시청자는 나레·대사·이름표로 소개된 이름만 안다). "
        "처음 보는 사람이 헷갈릴 곳만 골라라: "
        "장소 = 다른 장소로 넘어갔는데 어디인지·왜 거기 갔는지 그 줄이나 바로 앞 줄에서 안 들림 / "
        "인물 = 이야기에 중요한 인물이 처음 나오는데 누구인지(이름·관계) 안 들림 / "
        "원인 = 체포·죽음·이별·이사·사고·결혼·큰돈 같은 큰 사건의 이유가 안 들려서 왜 그렇게 됐는지 모름 / "
        "뜬금 = 앞뒤 이어짐 없이 갑자기 나온 말 / "
        "장면 = 죽음·사고·체포·고백·이별 같은 큰 사건을 [나레] 한 줄로만 말하고 그 장면을 보여 주는 [대사 자막]·[말 없는 원래 소리 장면]이 없어서 시청자가 갑자기? 하게 됨 / "
        "감정 = 인물이 마음과 반대로 말하거나(거절·거짓말·이별 통보) 크게 흔들리는데 그 속마음·이유가 안 들려서 왜 저러는지 모름. "
        "훅(예고) 구역, 같은 건물 안에서 방만 바뀐 것, 바로 다음 두 줄 안에서 풀리는 것, 앞에서 이미 나온 정보(앞 나레 목록을 확인), 영화가 일부러 숨겨 둔 반전(뒤에서 밝혀짐), 곁가지 인물의 사소한 일은 빼라. "
        "주인공 이야기 줄기를 끊는 것만, 많아야 6개. 장면·감정 문제는 꼭 짚어라. fix 는 이 글에 나온 사실만으로 써라 — 영화 내용을 짐작해 지어내지 마라. "
        "S 는 문제가 처음 생기는 줄 번호, why 는 시청자가 무엇을 모르는지 한 문장, fix 는 그 자리에 넣을 나레 한 문장(출발 비디오 여행 말투, 30자 안팎, 혼잣말·~고요 금지).\n")
out = []; i = 0; CH = 6500
while i < len(rows):
    j = i; n = 0
    while j < len(rows) and n < CH: n += len(rows[j][1]) + 1; j += 1
    before = [r for _, r in rows[:i] if "[나레]" in r]
    past = "\n".join(re.sub(r"  〔화면:.*", "", r) for r in before)[-2500:]
    prompt = RULE + (("\n앞에서 이미 나온 나레(참고만, 여기선 고르지 마):\n" + past + "\n") if past else "") + "\n이번에 읽을 부분:\n" + "\n".join(r for _, r in rows[i:j])
    prompt = prompt.replace('"', "'")
    r = subprocess.run([AGY, "-p", prompt, "--model", "gemini-3.8-flash-high", "--print-timeout", "300s", "--output-format", "json", "--disable-slash-commands", "--json-schema", SCH],
                       cwd=W, capture_output=True, timeout=400)
    o = r.stdout.decode("utf-8", "replace")
    try: jj = json.loads(o[o.find("{"):]); resp = jj.get("response") or ""; got = json.loads(resp[resp.find("{"):resp.rfind("}") + 1])["items"]
    except Exception as e: print("  실패", rows[i][0], "~", rows[j - 1][0], str(e)[:80], o[-300:]); got = []
    lo, hi = rows[i][0], rows[j - 1][0]
    hook = {k for k, x in enumerate(S) if k < next((j for j, y in enumerate(S) if y[0] == "ZONE" and y[1] == "main"), 0)}
    out += [g for g in got if lo <= g["S"] <= hi and g["S"] not in hook]
    print(f"S{lo}~S{hi}: {len([g for g in got if lo <= g['S'] <= hi])}개", flush=True)
    i = j
OK = CFG.get("cold_ok", {})
def key(k):
    x = S[k]; t = x[1] if x[0] == "N" else x[2] if x[0] == "D" else f"A{x[1]}"
    return f"S{k} " + str(t)[:12]
res = [dict(g, key=key(g["S"]), ok=OK.get(key(g["S"]))) for g in sorted(out, key=lambda g: g["S"]) if 0 <= g["S"] < len(S)]
json.dump(res, open("cold_read.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
left = [g for g in res if not g["ok"]]
print(f"안 본 사람 검사: {len(res)}개 (괜찮다고 적은 것 {len(res) - len(left)})")
for g in res: print(("  ✓ " if g["ok"] else "  ✗ ") + f"{g['key']} [{g['kind']}] {g['why']}\n      → {g['fix']}" + (f"\n      (괜찮음: {g['ok']})" if g["ok"] else ""))
sys.exit(1 if left else 0)
