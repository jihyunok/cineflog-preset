---
name: flip-check-edges
description: 영화리뷰 좌우반전 글자 검사는 조각 처음·가운데·끝 세 프레임으로 — 10-22 06 A판 지명 카드 놓침
metadata:
  type: feedback
---

2026-10-22 06 허큘리스 A판 3:56: 아테네 지명 자막 카드(「3 YEARS EARLIER / PALACE OF KING EURYSTHEUS, ATHENS」)가 조각 앞 1초에만 떠 있어 가운데 프레임 시트(flipsheet)로 못 잡고 거꾸로 나감. 사용자 텔레그램 "그냥 두고 다음부터 실수하지 말고 검수해."

- flipsheet.py 가 조각마다 처음·가운데·끝 세 프레임을 보여 준다(10-22 고침). 시트는 전부 눈으로.
- 지명·시대 자막 카드는 장면 첫머리에 페이드로 걸친다 — 장소가 바뀌는 첫 조각은 특히.

**Why:** 완성본에 거꾸로 된 글자가 나가면 바로 티가 남. 사용자가 "실수하지 말고 검수해"라고 함.
**How to apply:** 굽기 전 반전 글자 검사 단계마다. 이미 만든 편은 고치지 않음(사용자 "그냥 두고"). [[movie-review-preset]] [[ab-version-other-channel]]
