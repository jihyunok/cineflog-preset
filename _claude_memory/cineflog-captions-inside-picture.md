---
name: cineflog-captions-inside-picture
description: "시네플로그 mp4 자막(나레·대사)은 아래 검은 띠가 아니라 영화 그림 안쪽 아래에 — 10-12 \"대본은 영상 안에 넣어\""
metadata:
  type: feedback
---

2026-10-12 사용자: "대본은 영상 안에 넣어" (16 핀치 v6 를 보고).
- mp4 자막(N 경기천년제목 100 · D Stylish 104)은 그림(y 138~942) 안 아래쪽: ASS MarginV 165(글자 아래끝 약 y915). 검은 띠(MarginV 22)에 두지 않는다.
**Why:** 자막이 아래 검은 띠에 있으면 사용자가 원하는 꼴이 아니다.
**How to apply:** 시네플로그 새 편·고친 편 build 의 Style N·D MarginV 를 165 로. 캡컷 04 꼴 위치(y -0.741)는 사용자가 직접 맞춘 값이라 그대로. [[cineflog-channel]] [[dungdung-lecture-checklist]]

- ★같은 날 이어서 "화면아래위너무 자르지말고" → 박힌 자막 지우기 확대는 컷 통째가 아니라 **자막이 떠 있는 동안만**, 그 줄 위끝까지만(한 줄 1.28배·두 줄 1.39배). 평소는 살짝 크롭(1.05). build_v6.py cut() 의 overlay enable.
