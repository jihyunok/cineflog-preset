# -*- coding: utf-8 -*-
"""캡컷 드래프트의 「자막」 트랙을 「나레이션 자막」·「대사 자막」 두 트랙으로 나눈다. 글꼴·크기·색은 사용자가 캡컷에서 트랙째 고른다("글골크기내가 선택할거니까").
나레이션 오디오가 깔린 시간에 뜨는 자막 = 나레, 나머지 = 원본 대사.
사용(캡컷 끈 뒤): python capcut_split_subs.py [드래프트폴더...]  — 인자 없으면 시네플로그01~03 + 완성본 _캡컷 폴더."""
import copy, glob, json, os, shutil, sys, uuid
BAK = os.path.expanduser("~/volcano_work/시네플로그/_capcut_bak")
dirs = sys.argv[1:] or (sorted(glob.glob("D:/다운로드/CapCut Drafts/시네플로그0*")) +
                        sorted(glob.glob(os.path.expanduser("~/volcano_work/시네플로그/완성본/*_캡컷"))))

def split(d):
    if any(t.get("name") == "대사 자막" for t in d["tracks"]): return None
    narr = [(s["target_timerange"]["start"], s["target_timerange"]["start"] + s["target_timerange"]["duration"])
            for t in d["tracks"] if t["type"] == "audio" and t.get("name") == "나레이션" for s in t["segments"]]
    st = [t for t in d["tracks"] if t["type"] == "text" and t.get("name") == "자막"][0]
    mats = {m["id"]: m for m in d["materials"]["texts"]}
    dt = copy.deepcopy(st); dt.update({"id": str(uuid.uuid4()).upper(), "name": "대사 자막", "segments": []})
    st["name"] = "나레이션 자막"; keep = []
    for s in st["segments"]:
        mid = s["target_timerange"]["start"] + s["target_timerange"]["duration"] / 2
        if any(a <= mid < b for a, b in narr): keep.append(s); continue
        dt["segments"].append(s)
    st["segments"] = keep
    d["tracks"].insert(d["tracks"].index(st) + 1, dt)
    return len(keep), len(dt["segments"])

for D in dirs:
    tl = json.load(open(f"{D}/timeline_layout.json", encoding="utf-8"))["dockItems"][0]["timelineIds"][0]
    b = f"{BAK}/{os.path.basename(D)}"; os.makedirs(b, exist_ok=True)
    for p in (f"{D}/draft_content.json", f"{D}/Timelines/{tl}/draft_content.json"):
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8"))
        r = split(d)
        if r is None: print(os.path.basename(D), "이미 나뉨"); continue
        shutil.copy(p, f"{b}/{os.path.relpath(p, D).replace(os.sep, '__')}.before_split")
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        print(os.path.basename(D), os.path.relpath(p, D), "나레 자막", r[0], "· 대사 자막", r[1])
