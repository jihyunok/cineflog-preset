---
name: git-push-use-gh-credential
description: 깃허브 push 가 조용히 멈추면(Git Credential Manager 창 대기) gh 인증으로 밀어 넣는다 — cineflog-preset 10-17 실측
metadata:
  node_type: memory
  type: reference
  originSessionId: e5e1492c-0c2f-44e7-a90c-2405ab058d81
  modified: 2026-10-17T08:36:52.318Z
---

2026-10-17 jihyunok/cineflog-preset push 가 두 번 조용히 멈췄다(timeout 240초에도 출력 없음, `git fetch` 도 멈춤). credential.helper 가 `manager`(Git Credential Manager)라 화면 없는 셸에서 인증 창을 기다리는 것으로 보였다.

- 됨: `GIT_TERMINAL_PROMPT=0 git -c credential.helper= -c "credential.helper=!gh auth git-credential" push --progress origin master` (gh 는 jihyunok 로 로그인돼 있음, 토큰 repo 범위) → 67eed10..d177500, 17.8MB(글꼴 포함) 약 1분.
- 큰 push 는 run_in_background 로 돌리고 로그 파일로 확인.

관련: [[cineflog-remake-old-episodes]]
