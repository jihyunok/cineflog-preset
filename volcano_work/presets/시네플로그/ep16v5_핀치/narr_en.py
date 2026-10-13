# -*- coding: utf-8 -*-
"""나레 조각(narr/nNNN.json 글자)을 agy 로 영어 한 줄씩 옮긴다 — 제브 판정(나레그림_맞음.json)은 영어 state 가 가장 정확 (10-13).
결과 narr_en.json {ni: 영어}. 사용: python narr_en.py"""
import json, os, subprocess, tempfile
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
PL = json.load(open("narr_place.json"))
lines = {q["ni"]: "".join(json.load(open(f"narr/n{q['ni']:03d}.json", encoding="utf-8"))["chars"]) for q in PL}
W = os.path.join(tempfile.gettempdir(), "agy_narr"); os.makedirs(W, exist_ok=True)
SCH = os.path.join(W, "s.json")
json.dump({"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "ni": {"type": "integer"}, "en": {"type": "string"}}, "required": ["ni", "en"]}}}, "required": ["items"]}, open(SCH, "w", encoding="utf-8"))
out = json.load(open("narr_en.json", encoding="utf-8")) if os.path.exists("narr_en.json") else {}
todo = [(k, v) for k, v in lines.items() if str(k) not in out]
for i in range(0, len(todo), 15):
    part = todo[i:i + 15]
    prompt = ("도구·명령어 쓰지 말고 답해줘. 영화 「Finch」 리뷰 나레이션 줄들을 자연스러운 영어 한 문장씩으로 옮겨. 뜻만 정확히, 덧붙이지 말 것.\n"
              + "\n".join(f"{k}: {v}" for k, v in part))
    r = subprocess.run([AGY, "-p", prompt, "--print-timeout", "300s", "--output-format", "json", "--disable-slash-commands", "--json-schema", SCH],
                       cwd=W, capture_output=True, timeout=360)
    o = r.stdout.decode("utf-8", "replace")
    try: j = json.loads(o[o.find("{"):]); resp = j.get("response") or ""; got = json.loads(resp[resp.find("{"):resp.rfind("}") + 1])["items"]
    except Exception as e: print("  실패", part[0][0], str(e)[:80], o[-200:]); continue
    for it in got: out[str(it["ni"])] = it["en"]
    json.dump(out, open("narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("영어 나레", len(out), "/", len(lines))
