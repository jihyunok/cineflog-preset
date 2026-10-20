---
name: tts-call-saving
description: AI 스튜디오 TTS 는 호출 수로 한도 — 2,000자씩 묶어 한 번에 녹음하고 잘라 씀, 떨어진 줄도 한 묶음, 실패하면 자동 재시도 금지 (10-19)
metadata:
  type: feedback
---

★10-20 다른 PC(「대작」) 기억을 이 PC 로 가져옴(사용자 "시네플로그 프리셋에 없는거 찾아서 추가해"). 이 PC 채널 글자는 CINEFLOG 그대로 — [[cineflog-other-pc-daejak]].

2026-10-19 사용자: "tts는 호출수에따라 한도가 소진되지? 최대한 절감하는 방식으로 녹음하고 잘라"

- mkbatch.py 한 묶음 2,000자(옛 1,000), 떨어진 줄도 한 묶음(batches.json 4번째 칸 ids) → gem_split·gem_check 가 ids 순서로 자름.
- 같은 글 다시 녹음 금지(mkbatch 가 거름), 번호 밀림은 renum.py, 시험 녹음 안 함.
- page.js cineLoop 는 실패하면 멈춤(자동 재시도 없음) — 원인 보고 남은 묶음만.
- 쇼츠 나레는 롱폼 조각 재사용(1.35배), 없는 줄만 한 묶음.

**Why:** 무료 한도는 호출 수로 깎이고 16시(한국)에 풀린다.
**How to apply:** 녹음 전 batches.json 묶음 수를 먼저 세어 보고, 첫 2,000자 묶음이 끝까지 녹음됐는지 확인. 잘리면 1,500자로. [[movie-review-shorts-template]]
