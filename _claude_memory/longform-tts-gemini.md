---
name: longform-tts-gemini
description: 롱폼 나레 목소리는 앞으로 제미나이 3.8 TTS(agy 로) — 비싼 유료 TTS 쓰지 말 것 (10-07)
metadata:
  node_type: memory
  type: feedback
  originSessionId: ede7f3d9-0da7-4c8c-ad8d-5d62f937358d
  modified: 2026-10-07T01:53:16.263Z
---

2026-10-07 사용자: "롱폼하시면 타케쓰면 비싸니까 제미나이 3.8 tts 이거 앞으로 쓸거야 타입캐스트 쓰지말고 목소리"
- 롱폼(드라마 몰아보기·시네플로그 등) 나레는 제미나이 3.8 TTS. 타입캐스트·ElevenLabs 같은 유료 TTS 는 쓰지 않는다.
- 제미나이는 agy 로만(CLAUDE.md) — API 키 만들지 말 것. agy 에서 TTS 가 되는지 먼저 확인하고, 안 되면 사용자에게 말한다.

**Why:** 롱폼은 나레가 길어 유료 TTS 비용이 크다.
**How to apply:** 새 롱폼 편부터(드라마몰아보기 02 크래시~). 이미 나온 편은 다시 녹음하지 않는다. [[drama-binge-preset]] [[cineflog-channel]]
- 길: 크롬에서 aistudio.google.com/generate-speech, ★울트라 계정 「98」(/u/2/)로 — 사용자가 "구글스튜디오는 98로 들어가야지". 모델 Gemini 3.8 Flash TTS. 한국어 전용 목소리는 유료 키 필요라 기본 목소리 사용.
- 10-07 목소리 Ludo(Confident and clear, Low pitch) 샘플 듣고 사용자: "지금 이목소리도 좋은데".
- ★10-07 시네플로그 13편~ 사용자: "재미나이 원래하던 목소리로해 하 막 ㄴ일래븐랩스로 넘어가줘" → 제미나이 Ludo 로 하되, **AI 스튜디오가 막히면 ElevenLabs(Minjun)로 넘어가도 된다**(사용자 허락). 넘어가면 어느 편·몇 조각인지 보고한다.
