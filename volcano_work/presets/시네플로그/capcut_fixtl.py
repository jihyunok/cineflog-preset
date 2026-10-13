# -*- coding: utf-8 -*-
"""캡컷 드래프트가 안 열리던 원인 고침: Timelines/project.json 이 틀의 타임라인 번호를 가리키던 것을
timeline_layout.json 의 실제 번호로 맞추고, 틀에서 딸려 온 파일(draft.extra·template.json·draft_virtual_store.json)은 백업 폴더로 옮긴다.
캡컷을 끈 뒤에 돌린다. 인자 없으면 시네플로그01~03 + 완성본 _캡컷 폴더 3개."""
import glob, json, os, sys, shutil, uuid, time
BAK = os.path.expanduser("~/volcano_work/시네플로그/_capcut_bak")
dirs = sys.argv[1:] or (sorted(glob.glob("D:/다운로드/CapCut Drafts/시네플로그0*")) +
                        sorted(glob.glob(os.path.expanduser("~/volcano_work/시네플로그/완성본/*_캡컷"))))
for D in dirs:
    tl = json.load(open(f"{D}/timeline_layout.json", encoding="utf-8"))["dockItems"][0]["timelineIds"][0]
    pj = f"{D}/Timelines/project.json"; p = json.load(open(pj, encoding="utf-8"))
    b = f"{BAK}/{os.path.basename(D)}"; os.makedirs(b, exist_ok=True)
    shutil.copy(pj, f"{b}/project.json.orig")
    now = int(time.time() * 1e6)
    p.update({"id": str(uuid.uuid4()).upper(), "main_timeline_id": tl, "create_time": now, "update_time": now})
    p["config"].setdefault("hdr_vivid", False)
    p["timelines"] = [{"create_time": now, "id": tl, "is_marked_delete": False, "name": "타임라인 01", "update_time": now}]
    json.dump(p, open(pj, "w", encoding="utf-8"), ensure_ascii=False)
    for x in os.listdir(f"{D}/Timelines"):
        q = f"{D}/Timelines/{x}"
        if os.path.isdir(q) and x != tl and not os.listdir(q): os.rmdir(q)          # 캡컷이 만든 빈 폴더
    for f in (f"{D}/Timelines/{tl}/draft.extra", f"{D}/Timelines/{tl}/template.json", f"{D}/draft_virtual_store.json"):
        if os.path.exists(f): shutil.move(f, f"{b}/{os.path.relpath(f, D).replace(os.sep, '__')}")
    print(os.path.basename(D), "타임라인", tl, "·", os.listdir(f"{D}/Timelines"))
