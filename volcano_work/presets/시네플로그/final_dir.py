# -*- coding: utf-8 -*-
"""완성본 넣는 곳 — 이 PC 는 ~/volcano_work/시네플로그/완성본 (기억 「완성본만 남긴다」).
다른 PC(「대작」, 10-19 사용자 "영화리뷰 최종본으로 넣어줘")는 저장소 맨 위 「영화리뷰 최종본」 — 10-20 그 PC 도구를 가져오며 이 파일만 이 PC 경로로 바꿨다.
capcut_to_final·thumb_deliver·shorts/build_shorts 등이 FINAL 을 읽는다. 환경 변수 FINAL_DIR 가 있으면 그것."""
import os
FINAL = os.environ.get("FINAL_DIR") or os.path.expanduser("~/volcano_work/시네플로그/완성본")
