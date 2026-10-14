# -*- coding: utf-8 -*-
"""원본 대사 줄 표: 박힌 자막 줄(subev, 옛 ep17 이 같은 파일에서 잰 것) 마다 Speechmatics 영어 낱말 + 옛 우리 자막(ko17). → lines.json"""
import json
EV = json.load(open("subev.json")); KO = json.load(open("ko17.json", encoding="utf-8"))
SW = json.load(open("src_sm.json", encoding="utf-8"))["words"]
out = []; used = set()
for ev in EV:
    ws = [(k, w) for k, w in enumerate(SW) if k not in used and ev["s"] - 0.6 <= (w["start"] + w["end"]) / 2 <= ev["e"] + 0.3]
    for k, _ in ws: used.add(k)
    out.append({"id": ev["id"], "s": ev["s"], "e": ev["e"], "en": " ".join(w["word"] for _, w in ws),
                "ws": round(ws[0][1]["start"], 2) if ws else None, "we": round(ws[-1][1]["end"], 2) if ws else None, "ko": KO.get(str(ev["id"]))})
json.dump(out, open("lines.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("줄", len(out), "· 영어 있음", sum(1 for x in out if x["en"]), "· 옛 우리 자막", sum(1 for x in out if x["ko"]), "· 줄에 안 붙은 낱말", len(SW) - len(used))
