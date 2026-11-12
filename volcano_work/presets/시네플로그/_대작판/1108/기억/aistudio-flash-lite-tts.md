---
name: aistudio-flash-lite-tts
description: "AI 스튜디오 녹음 모델은 gemini-3.8-flash-lite-tts + Ludo (11-08) — 옛 flash-tts 는 Quota 창, 사용자 「한도가 아니야」"
metadata:
  type: feedback
---

영화·드라마 나레 녹음은 AI 스튜디오 `generate-speech?model=gemini-3.8-flash-lite-tts` 에서 Ludo 로 한다.

**Why:** 11-08 옛 `gemini-3.8-flash-tts` 가 Run 즉시 「Quota limit reached」 창 → 내가 한도라고 보고했더니 사용자 「한도가 아니야」, 사용자가 탭을 Flash Lite TTS 로 바꿔 시험한 뒤 「맞아」. 말 빠르기는 옛 모델과 같음.

**How to apply:** 녹음 전 탭 URL 모델 확인. Quota 창이 떠도 한도로 단정하지 말고 모델·화면부터 확인 후 텔레그램으로 보이는 그대로 알림. 「API 키 연결」은 절대 누르지 않음. 관련 [[aistudio-failure-notify]] [[volcanokit-tts]].
