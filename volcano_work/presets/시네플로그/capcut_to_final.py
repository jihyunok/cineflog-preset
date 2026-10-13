# -*- coding: utf-8 -*-
"""캡컷 드래프트를 완성본 폴더로 복사 — 안쪽 경로를 캡컷 표준 자리표시자로 바꿔 어디로 옮겨도 열리게 한다.
사용: python capcut_to_final.py 시네플로그02 02_패밀리플랜"""
import os, shutil, sys, glob
ROOT = "D:/다운로드/CapCut Drafts"
PH = "##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##"
name, ep = sys.argv[1], sys.argv[2]
src = f"{ROOT}/{name}"
dst = os.path.expanduser(f"~/volcano_work/시네플로그/완성본/{ep}_캡컷")
if os.path.exists(dst): shutil.rmtree(dst)
shutil.copytree(src, dst)
n = 0
for p in [f"{dst}/draft_content.json"] + glob.glob(f"{dst}/Timelines/*/draft_content.json"):
    s = open(p, encoding="utf-8").read()
    for pre in (src, src.replace("/", "\\\\"), src.replace("/", "\\")):
        n += s.count(pre); s = s.replace(pre, PH)
    open(p, "w", encoding="utf-8").write(s)
open(f"{dst}/캡컷에서_여는법.txt", "w", encoding="utf-8").write(
    f"★이 컴퓨터에는 이미 캡컷 프로젝트 목록에 「{name}」으로 들어 있습니다. 캡컷을 켜고 그걸 여세요.\n"
    "★캡컷 설정의 「프로젝트 위치」를 이 폴더로 바꾸지 마세요(바꾸면 목록이 텅 빕니다).\n\n"
    "다른 컴퓨터에서 열 때:\n"
    f"1. 이 폴더({ep}_캡컷)를 통째로 그 컴퓨터의 캡컷 프로젝트 폴더 「안에」 복사합니다.\n"
    f"   (캡컷 > 설정 > 프로젝트 위치에 적힌 폴더. 이 컴퓨터는 {ROOT})\n"
    "2. 캡컷을 껐다 켜면 프로젝트 목록에 나옵니다.\n"
    "3. 영상·나레·음악·자막 트랙이 따로 들어 있어 자유롭게 고칠 수 있습니다.\n")
print(dst, "경로", n, "곳 바꿈")
