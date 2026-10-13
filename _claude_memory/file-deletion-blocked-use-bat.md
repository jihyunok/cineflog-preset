---
name: file-deletion-blocked-use-bat
description: 자동 모드에선 삭제도, 정리 스크립트 쓰기도 막힌다 — 첫 줄에 "Shift+Tab 으로 자동 모드 끄고 '다시 해'" 안내. 한글 ps1 함정·Kill 별칭 함정
metadata:
  node_type: memory
  type: feedback
  originSessionId: 21e0c184-f641-4619-bcb4-d2ab1fcb0a4b
  modified: 2026-10-13T05:26:36.502Z
---

자동 모드 분류기가 Remove-Item/rm 삭제를 "Irreversible Local Destruction" 으로 매번 막는다 (2026-09-21 C 드라이브 정리 때 3번 연속 차단). 사용자는 `! powershell ...` 한 줄을 적으라는 안내에 "삭제해줘 뭐를 적으라고" 하며 짜증을 냈다.

★2026-10-13: 자동 모드에선 **정리용 ps1/bat 파일을 쓰는 것까지** 막혔다(Write 도 차단). 조사만 길게 하다가 막혀서 사용자 "너 머하니 삭제하라는데".

**Why:** 사용자는 명령어를 직접 입력하는 걸 원하지 않고, 지우라면 바로 지워지길 원한다.

**How to apply:**
- 삭제 요청이 오면 **첫 줄에** "자동 모드에선 제가 못 지워요 — 입력창에서 Shift+Tab 으로 자동 모드를 끄고 '다시 해' 라고 쳐 주세요, 허락 창만 누르시면 됩니다" 라고 말한다. 지울 목록·완성본 대조는 그다음.
- 10-13 에 통한 방법: 자동 모드가 꺼진 뒤 scratchpad 에 ps1 을 쓰고 내가 `-DryRun` 으로 돌려 합계 확인 → 실제 실행(run_in_background). 관리자 일(powercfg /h off)은 `Start-Process powercfg -ArgumentList '/h','off' -Verb RunAs -Wait` → 사용자는 UAC 「예」만.
- 사용자가 직접 돌리는 bat 가 필요할 때: `.bat` 는 **ASCII 만, CRLF**(한글 넣으면 CP949 로 깨짐), `.ps1` 은 **UTF-8 BOM**. 문자열 안 `$n개` 는 `$($n)개`.
- ★ps1 함수 이름을 `Kill` 로 짓지 말 것 — PowerShell 기본 별칭(Stop-Process)이 함수보다 먼저 불려 아무것도 안 지우고, ErrorAction SilentlyContinue 면 오류도 안 보인다(10-13 미리보기 0GB 의 원인). `Remove-Work` 처럼 동사-명사로.
- `[Parser]::ParseFile` 로 문법 검사. 결과 확인 때 `Test-Path C:\hiberfil.sys` 는 비관리자에서 false — `Get-ChildItem C:\ -Force` 로 확인.

관련: [[c-drive-cleanup-2026-10-13]] · [[no-work-files-only-final]] · [[irreversible-check-first]]
