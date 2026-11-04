---
name: cineflog-script-flow-1104
description: "시네플로그 새 편 대본 흐름 (11-04, nm2240/movie-review 에서 합침) — movie_template 로 시작, 배급사 먼저·줄기·명장면·통독·부드러운 말투·d_fill, 25분 목표(모자라면 묻기)"
metadata:
  node_type: memory
  type: project
  originSessionId: 726f188f-8101-41ed-ba31-0aa0b8dcf49f
  modified: 2026-11-04T07:45:26.486Z
---

2026-11-04 사용자: "내가준 깃허브에 대본흐름을 좀 바꿨대 확인해봐" → 비교 보고 뒤 "응" → "합치고 깃허브에 저장해".

새 편은 `presets/시네플로그/movie_template/` 복사로 시작한다. 규칙 전문은 프리셋 README 맨 앞 「11-04 대본 흐름」.
- 순서: 원본 받으면 배급사 먼저(`blocked_studios.txt`) → `_줄기.md`(15~20 사건·인물 표기·명장면) → 토막 → 편집자 통독 → flow_check·cold_read·jev_fact·name_check → 녹음.
- 말투: 명사형 15% 이하·연달아 금지, 연결형·「~하죠」로 부드럽게(옛 35~40% 폐기).
- 대사: ep.json d_fill 3.0, 상대 말 3초 안이면 묶기. 짧은 나레 섞기, 핵심 장면 cont 10~15곳.

**Why:** 작업자 4명이 토막을 따로 써서 사건 사이 원인·결과가 잘린다는 진단. 저쪽 사용자가 38 노벰버 맨을 보고 확정한 방식이다.
**How to apply:**
- 길이는 저쪽 18분 허용을 따르지 않는다. 25분 목표, 곁가지로 채우지 않고, 모자라면 숫자를 보여 주고 묻는다. [[cineflog-length-20-30]]
- 이름표·「대작」 글자·계정은 계속 뺀다. [[cineflog-other-pc-daejak]]
- cont 이음은 3초 간격 예외라 소유권 주장 시험을 아직 못 했다. 첫 편은 일부공개로 먼저 확인한다. [[cineflog-cid-transform-all-windows]]
- 저쪽 판이 또 오면 통째로 덮지 말고 3-way 로 합친다(fill·이름표가 켜진다). `nm2240/movie-review` 는 비공개라 jihyunok 으로 404, 사용자가 zip 을 받아 준다.
- plan_v9 의 여운 기본값은 ep.json 에 d_fill 있는 편만 켜진다. 옛 편 다시 계획은 조각까지 그대로다.
