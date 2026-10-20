# -*- coding: utf-8 -*-
"""틀 드래프트에서 딸려 온 클라우드 연결 정보를 지운다 (캡컷 「복제」가 "비정상적인 접근"으로 막히던 원인).
사용: python capcut_uncloud.py [--root]  (--root 는 캡컷을 끈 뒤에만: 목록 root_meta_info.json 도 고침)"""
import json, glob, os, sys, shutil
CLEAN = {"cloud_package_completed_time": "", "tm_draft_cloud_completed": "", "tm_draft_cloud_entry_id": -1,
         "tm_draft_cloud_modified": 0, "tm_draft_cloud_parent_entry_id": -1, "tm_draft_cloud_space_id": -1,
         "tm_draft_cloud_user_id": -1, "cloud_draft_sync": False, "cloud_draft_cover": False}
def fix(d):
    for k in CLEAN:
        if k in d: d[k] = CLEAN[k]
paths = glob.glob("D:/다운로드/CapCut Drafts/시네플로그*/draft_meta_info.json") + \
        glob.glob(os.path.join(__import__("final_dir").FINAL, "*_캡컷", "draft_meta_info.json"))
for p in paths:
    m = json.load(open(p, encoding="utf-8")); fix(m)
    json.dump(m, open(p, "w", encoding="utf-8"), ensure_ascii=False); print("meta", p)
if "--root" in sys.argv:
    R = os.path.expanduser(r"~/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/root_meta_info.json")
    shutil.copy(R, R + ".uncloud.bak")
    r = json.load(open(R, encoding="utf-8"))
    for e in r["all_draft_store"]:
        if e.get("draft_name", "").startswith("시네플로그"): fix(e); print("root", e["draft_name"])
    json.dump(r, open(R, "w", encoding="utf-8"), ensure_ascii=False)
