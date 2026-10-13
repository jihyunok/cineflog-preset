---
name: no-work-files-only-final
description: 작업 파일을 volcano_work 에 쌓지 말 것 — 완성본만 남기고 중간 파일은 임시 폴더에서 쓰고 버린다 (용량)
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7c596645-6d90-4027-bece-16e710820c93
  modified: 2026-09-28T05:12:36.309Z
---

2026-09-28 사용자: "완성본만 주면 되자나 이게 용량을 너무 먹어" (영상 ID 이름 폴더가 volcano_work 에 잔뜩 쌓인 화면을 보여주며 "이런거왜이렇게 만들어?")

**Why:** 디스크가 꽉 차서(09-26 0바이트) 사용자가 직접 1만여 개 파일을 지웠다. 영상 ID 폴더·중간 파일은 알아볼 수도 없고 용량만 먹는다.

**How to apply:**
- 받은 원본·프레임·나레 wav·중간 mp4 는 세션 scratchpad(임시 폴더)에서만 다룬다.
- volcano_work 에는 `<채널>/완성본/번호_제목.mp4` 만 남긴다. 영상 ID 이름 폴더를 새로 만들지 않는다.
- 끝나면 임시 파일 정리용 bat 를 준다([[file-deletion-blocked-use-bat]]).

관련: [[deliver-only-the-final-video]] · [[fright-vault-diagnosis-2026-09-28]]
