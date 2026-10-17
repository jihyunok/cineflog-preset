---
name: thumbnail-options-next-to-final
description: "★★10-17 \"섬네일은 왜 같은 파일안에 안넣니 찾기힘들어\" — 썸네일 보기(고르기 전 후보 포함)는 작업 폴더에만 두지 말고 완성본 폴더 영상 옆에 같은 앞머리로"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 341d4b93-855c-4e6d-8902-a137da5ac392
  modified: 2026-10-17T03:22:47.007Z
---

2026-10-17 사용자(시네플로그 04 위드아웃 리모스 완성 보고 뒤): "잘만들었어 그런데 섬네일은 왜 같은 파일안에 안넣니 찾기힘들어"
— 나는 썸네일 보기 5장을 작업 폴더 `D:/cine_work/ep04v2_…/썸네일_보기2_ABCDE.jpg` 에만 두고 경로만 알려 줬다.

**Why:** 사용자는 완성본 폴더를 열어 영상·업로드 글·썸네일을 한곳에서 본다. 작업 폴더 경로는 찾기 힘들다.
**How to apply:** 썸네일 보기를 만들면 곧바로 `<채널>/완성본/` 에 영상과 같은 앞머리로 넣는다 — `NN_제목_썸네일보기_A_문구.jpg` … + A~E 글자 붙은 `NN_제목_썸네일보기_한눈에.jpg`. 시네플로그는 `presets/시네플로그/thumb_deliver.py <보기 폴더> <NN_제목>`, 고르면 `--pick <NN_제목> A [B]`(→ _썸네일1·2.jpg, 남은 보기는 완성본/_옛/썸네일보기/). 다른 채널도 사용자가 볼 것(썸네일·업로드 글)은 완성본 옆에. 보고할 때는 완성본 폴더 이름을 말한다. [[cineflog-thumbnail-red-urgent]] [[deliver-only-the-final-video]] [[cineflog-04-without-remorse-remake]]
