# -*- coding: utf-8 -*-
"""일본어판 캡컷: capcut_style04 의 크기·기울임·색·테두리·위치·4K 필터를 그대로 옮기고, 글꼴만 일본어 글꼴로 바꾼다.
2026-10-05 사용자: "일본어판도 글자크기는 내가 정한대로해줘 위치랑" / "일본어 글자체는 상관없는데 크기는 좀 키워" / "나래이션이랑 대사글자는 다른 글자체로"
나레 = Noto Sans JP Black, 대사 = Yu Gothic Bold, 로고 = 04 그대로. 사용(캡컷에서 그 드래프트를 닫고): py capcut_style04_jp.py <드래프트폴더>"""
import json, os, sys
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "capcut_style04.py")
code = open(SRC, encoding="utf-8").read().split("\nfor D in sys.argv[1:]:")[0]
g = {"__file__": SRC}; exec(compile(code, SRC, "exec"), g)
FONT = {"나레이션 자막": os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/NotoSansJP-Black.ttf").replace("\\", "/"),
        "대사 자막": "C:/Windows/Fonts/YuGothB.ttc"}
def jp(d):
    M = {m["id"]: m for m in d["materials"]["texts"]}; n = 0
    for t in d["tracks"]:
        f = FONT.get(t.get("name")) if t["type"] == "text" else None
        if not f: continue
        for s in t["segments"]:
            m = M[s["material_id"]]; m.update(font_path=f, font_resource_id="", fonts=[])
            c = json.loads(m["content"])
            for st in c["styles"]: st["font"] = {"path": f, "id": ""}
            m["content"] = json.dumps(c, ensure_ascii=False); n += 1
    return n
for D in sys.argv[1:]:
    if os.path.exists(f"{D}/.locked"): print(os.path.basename(D), "캡컷에서 열려 있음 — 닫고 다시"); continue
    tl = json.load(open(f"{D}/timeline_layout.json", encoding="utf-8"))["dockItems"][0]["timelineIds"][0]
    for p in (f"{D}/draft_content.json", f"{D}/Timelines/{tl}/draft_content.json"):
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8")); a = g["apply"](d); b = jp(d)
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        print(os.path.basename(D), os.path.relpath(p, D), "04꼴", a, "· 일본어 글꼴", b)
