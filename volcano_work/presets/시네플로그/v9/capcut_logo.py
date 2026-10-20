# -*- coding: utf-8 -*-
"""캡컷 드래프트의 「로고」 트랙(「대작」)을 영상 워터마크(brand/대작_워터마크.png)와 같은 꼴로 — 지마켓 산스 굵게 · 금색 · 어두운 테두리.
10-20 텔레그램 "대작에 왕관은 빼고 처음세 넣었던 기호 넣어. 색상은 지금처럼해" · "쇼츠 롱 둘다 적용해. 아래 왼쪽으로 조금 옮겨".
capcut_style04.py 가 로고 꼴을 옛 CINEFLOG 꼴로 덮으므로 그 뒤에 돌린다(위치는 style04 자리에서 아래 왼쪽으로 조금).
사용(캡컷에서 그 드래프트를 닫고): python capcut_logo.py <드래프트폴더>
★다른 PC(「대작」)에서 10-20 가져옴 — 이 PC 는 ep.json "brand_png" 워터마크 그림을 쓰는 편만 돌린다(기본 CINEFLOG 글자 편은 style04 꼴 그대로)."""
import glob, json, os, sys
FONT = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/GmarketSansTTFBold.ttf").replace("\\", "/")
GOLD, EDGE = [1.0, 0.76, 0.1], [0.16, 0.1, 0.0]
D = sys.argv[1]
for p in [f"{D}/draft_content.json"] + glob.glob(f"{D}/Timelines/*/draft_content.json"):
    d = json.load(open(p, encoding="utf-8")); M = {m["id"]: m for m in d["materials"]["texts"]}; n = 0
    for t in d["tracks"]:
        if t.get("name") != "로고": continue
        for s in t["segments"]:
            m = M[s["material_id"]]; c = json.loads(m["content"])
            for st in c.get("styles", []):
                st["fill"] = {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": GOLD}}}
                st["font"] = {"id": "", "path": FONT}
                st["strokes"] = [{"content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": EDGE}}, "width": 0.1}]
            m.update({"content": json.dumps(c, ensure_ascii=False), "font_path": FONT, "text_color": "#FFC21A", "border_color": "#281900", "border_width": 0.1,
                      "font_id": "", "font_resource_id": "", "fonts": []})
            tr = s.setdefault("clip", {}).setdefault("transform", {"x": 0.0, "y": 0.0})
            tr["x"] = round(tr.get("x", 0.86) - 0.035, 4); tr["y"] = round(tr.get("y", 0.87) - 0.05, 4)   # 아래 왼쪽으로 조금(영상 워터마크 72:54 와 같은 쪽)
            n += 1
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    print(os.path.relpath(p, D), "로고", n)
