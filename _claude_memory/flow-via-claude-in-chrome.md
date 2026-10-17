---
name: flow-via-claude-in-chrome
description: "10-07 사용자 \"플로우킷하지말고 클로드인크롬으로 할거야\" — 플로우 그림은 flowkit 말고 Claude in Chrome 으로 화면 조작"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 639ef6e0-5c1f-45ef-9944-b3e5e7b59d04
  modified: 2026-10-07T02:12:58.327Z
---

2026-10-07 사용자(스카토롱폼 13편 그림 중): "플로우킷하지말고" "클로드인크롬으로 할거야"
- 구글 플로우 그림은 flowkit 서버(flowimg.py) 대신 Claude in Chrome(mcp__claude-in-chrome__*) 으로 플로우 화면을 직접 조작해 만든다.

**Why:** 사용자 지시 (flowkit 은 하루 한도·CAPTCHA 로 자주 막혔다).
**How to apply:** 스카토롱폼 등 플로우를 쓰는 모든 작업. flowkit 을 켜지 말 것. [[flowkit-installed]] [[sukatto-longform-preset]]

★10-07 확인: Claude in Chrome 이 붙은 크롬은 하나(기본 계정 gihyun4175)뿐이지만 98wedding@gmail.com(울트라)도 로그인돼 있다 → 주소에 **/u/2/** (또는 ?authuser=2) 를 붙이면 98wedding 으로 열린다. 스카토롱폼 플로우 프로젝트: https://flow.google.com/u/2/project/2d43e9d0-c005-43b8-8544-a60af1794721 (「1.아키일본롱폼」). authuser=0 은 gihyun4175, 1 은 ibujin853 — 이 계정들로 열지 말 것(사용자 짜증).

★10-08: 연결이 끊긴 뒤 크롬이 두 개(deviceId ea2189e4…「DESKTOP-9TDJ0IC/Browser 2」, 96138e4d…「e/Browser 1」) 붙었다. 작업 스크립트(localStorage s1~s5·g1·g2·t1·t2)가 들어 있는 원래 플로우 탭(tabId 1751837252)은 **ea2189e4** 쪽이다. 끊기면 list_connected_browsers → select_browser(ea2189e4…) → tabs_context_mcp. 사용자는 이 일로 되묻는 걸 원하지 않았다("다시해"). 새 크롬에서 열면 localStorage 가 비어 있어 스크립트를 다시 넣어야 한다.

★10-08: 참고그림 고르기 창은 제목으로 검색하는데, 플로우가 붙이는 자동 제목이 겹치면(예: 두 인물 모두 「Man in suit standing」) 검색에 하나만 나온다 → 편집 화면 왼쪽 위 제목을 눌러 고쳐 쓰면 된다(예: 「Husband in gray suit Koji」). 인물 기본 그림을 만든 직후 고르기 창 목록에서 겹치는 제목이 없는지 먼저 본다.
