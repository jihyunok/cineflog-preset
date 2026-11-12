---
name: youtube-guideline-title-thumb
description: "★11-02 제목·썸네일은 유튜브 가이드라인 안 걸리게 — 존X 같은 가린 욕도 금지, 성적·잔혹·혐오 말, 피·노출 그림, 낚시 금지 (영화·드라마, yt_safe.py)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: de3950af-0899-4344-a3a2-c0b42fdaf23e
  modified: 2026-11-02T01:29:29.227Z
---

사용자(11-02, 영화 세션): 「앞으로 만드는 영상은 제목이랑 썸네일 유튜브 가이드라인 위반 안되게 해줘」.

- 글자: 욕·비속어 금지(10-16 사용자 견본 「진짜 존X 잘싸움」 스타일의 「존X」도 이제 안 씀 → 「역대급 긴장감」「숨 막히는 긴장감」「소름 돋는 반전」). 성적인 말·잔혹한 묘사·혐오 표현 금지.
- 그림: 피·시체·잔혹 장면, 노출·성적 장면, 아이 위협, 총구 정면은 썸네일로 안 씀.
- 낚시 금지: 영상에 없는 장면·사건, 실화 아닌데 실화.

**Why:** 채널 제재·수익 제한 피하려고.
**How to apply:** 영화리뷰·드라마 = 저장소 `v9/yt_safe.py` 가 thumb_quote.py·title_name.py 에서 자동으로 멈춤(README 맨 앞 규칙). 다른 프리셋 썸네일·제목에도 같은 기준으로 직접 판단. 이미 만든 편은 사용자가 고쳐 달라고 할 때만([[instructions-current-video-only]]).
