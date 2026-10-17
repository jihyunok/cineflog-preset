---
name: cineflog-logo-zoom
description: "10-14 \"로고는 화면키워\" — 원본에 박힌 로고·워터마크(AYA 등)는 가리거나 흐리지 말고 화면 확대로 잘라낸다"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e91dc7e8-0158-4dc4-b763-6912fa14b949
  modified: 2026-10-14T09:04:04.502Z
---

2026-10-14 사용자(02 패밀리 플랜 원본에 오른쪽 위 「AYA」 로고): "로고는 화면키워".

**Why:** 덮개·블러는 티가 나고, 확대는 2차 편집(확대)과 같이 되어 자연스럽다.
**How to apply:** 원본 프레임에서 로고 자리를 재서 ep.json `logo: [x0,y0,x1,y1]` 에 적으면 build_v9 가 기본 확대·박힌 자막 확대 모두 로고 아래부터 자른다. 로고가 크거나 가운데에 가까워 확대로 안 빠지면 먼저 사용자에게 말한다. 썸네일도 로고가 안 들어가게 자른다. [[cineflog-01-02-remake]] [[dungdung-lecture-checklist]]
