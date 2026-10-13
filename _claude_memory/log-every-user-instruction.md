---
name: log-every-user-instruction
description: "사용자가 말한 지시·되물림은 한 마디도 빠뜨리지 말고 저장소 문서에 그대로 박제한다"
metadata:
  node_type: memory
  type: feedback
---

사용자가 작업 중에 한 **말·지시·되물림을 전부** `volcano_work/docs/` 에 박제한다.
(2026-09-08 사용자 지시: "내가 말한거 다 박제해")

**Why:** 같은 지적을 두 번 하게 만들지 않기 위해서다. 실제로 "인물이 잘린다" 는 지적을
6편에서 두 번 들었다. 요약하지 말고 **사용자가 쓴 말 그대로** 남겨야 다음 세션이 판단할 수 있다.

**How to apply:** 규칙이 될 만한 것은 `docs/PLAYBOOK.md` 의 해당 절에,
요청·되물림 이력은 `docs/SESSION-LOG.md` 에 **원문 인용으로** 적고 커밋한다.
[[always-commit-session-record]] 의 강화판이다 — 그건 '배운 것', 이건 '사용자가 한 말'이다.

관련: [[always-commit-session-record]] · [[speaker-centered-in-frame]]
