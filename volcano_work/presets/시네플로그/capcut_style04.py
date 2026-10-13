# -*- coding: utf-8 -*-
"""사용자가 캡컷에서 직접 맞춘 시네플로그04 드래프트의 꼴을 다른 드래프트에 그대로 옮긴다 (2026-10-03 "이렇게 세팅해줘" / "4번까지는 수정했으니 5.6번 수정해줘").
옮기는 것: 나레이션 자막(경기천년제목B)·대사 자막(나다스탈리크)·로고(CINEFLOG) 의 글꼴·크기·기울임·색·테두리·위치, 필터 트랙(4K, 세기 0.50, 전 구간).
글자 내용·시간은 그대로. 사용(캡컷에서 해당 드래프트를 닫은 뒤): py capcut_style04.py <드래프트폴더>..."""
import copy, json, os, shutil, sys, uuid
REF = "D:/다운로드/CapCut Drafts/시네플로그04/draft_content.json"
if not os.path.exists(REF):   # 다른 컴퓨터(이식팩): 함께 들어 있는 04 꼴 사본
    REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "시네플로그04_꼴.json")
BAK = os.path.expanduser("~/volcano_work/시네플로그/_capcut_bak")
MAT_KEYS = ("font_size", "font_path", "italic_degree", "fonts", "font_resource_id", "font_source_platform", "fixed_width", "text_color", "border_width", "border_color")
nid = lambda: str(uuid.uuid4()).upper()

ref = json.load(open(REF, encoding="utf-8"))
RM = {m["id"]: m for m in ref["materials"]["texts"]}
TPL = {}
for t in ref["tracks"]:
    if t["type"] == "text":
        s = t["segments"][0]; TPL[t["name"]] = (s, RM[s["material_id"]])
RF = [t for t in ref["tracks"] if t["type"] == "filter"][0]
REF_FX = {e["id"]: e for e in ref["materials"]["effects"]}[RF["segments"][0]["material_id"]]

def apply(d):
    M = {m["id"]: m for m in d["materials"]["texts"]}; n = 0
    for t in d["tracks"]:
        if t["type"] != "text" or t.get("name") not in TPL: continue
        ts, tm = TPL[t["name"]]; st0 = json.loads(tm["content"])["styles"][0]
        for s in t["segments"]:
            m = M[s["material_id"]]
            for k in MAT_KEYS:
                if k in tm: m[k] = copy.deepcopy(tm[k])
            txt = json.loads(m["content"])["text"]; st = copy.deepcopy(st0); st["range"] = [0, len(txt)]
            m["content"] = json.dumps({"text": txt, "styles": [st]}, ensure_ascii=False)
            s["clip"] = copy.deepcopy(ts["clip"]); n += 1
    d["tracks"] = [t for t in d["tracks"] if t["type"] != "filter"]
    fx = copy.deepcopy(REF_FX); fx["id"] = nid()
    d["materials"]["effects"] = [e for e in d["materials"].get("effects", []) if e.get("type") != "filter"] + [fx]
    ft = copy.deepcopy(RF); ft["id"] = nid(); seg = ft["segments"][0]
    seg.update({"id": nid(), "material_id": fx["id"], "target_timerange": {"start": 0, "duration": d["duration"]}, "track_render_index": len(d["tracks"])})
    d["tracks"].append(ft)
    return n

for D in sys.argv[1:]:
    if os.path.exists(f"{D}/.locked"): print(os.path.basename(D), "캡컷에서 열려 있음 — 닫고 다시"); continue
    tl = json.load(open(f"{D}/timeline_layout.json", encoding="utf-8"))["dockItems"][0]["timelineIds"][0]
    b = f"{BAK}/{os.path.basename(D)}"; os.makedirs(b, exist_ok=True)
    for p in (f"{D}/draft_content.json", f"{D}/Timelines/{tl}/draft_content.json"):
        if not os.path.exists(p): continue
        shutil.copy(p, f"{b}/{os.path.relpath(p, D).replace(os.sep, '__').replace('/', '__')}.before_style04")
        d = json.load(open(p, encoding="utf-8")); n = apply(d)
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        print(os.path.basename(D), os.path.relpath(p, D), "자막·로고", n, "개 + 4K 필터")
