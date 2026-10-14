---
name: cineflog-no-black-tail
description: "10-14 \"영상 끝나고 10초넘게 시커먼화면이 나오는거확인하고 지워\" — 롱폼 끝에 음원 15초 검은 화면 넣지 말 것"
metadata:
  type: feedback
---

2026-10-14 17 그레이하운드 v12 끝에 「아웃트로 뒤 음원 15초」(강의 체크리스트 6번)로 검은 화면 16초가 붙어 있었다. 사용자: "영상 끝나고 10초넘게 시커먼화면이 나오는거확인하고 지워".

**Why:** 시청자가 보기엔 영상이 끝났는데 검은 화면만 흐른다.

**How to apply:** 마지막 나레 1.5초 뒤 끝(음악 2초·화면 1초 페이드). presets/시네플로그/v9/build_v9.py·capfix.py 고침. 다른 롱폼 프리셋에도 끝 검은 화면 음원이 있으면 같은 규칙. 건네기 전 blackdetect 로 끝 검은 화면 확인.

관련: [[dungdung-lecture-checklist]] [[cineflog-greyhound-next]]
