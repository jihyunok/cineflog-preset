---
name: cineflog-youtube-channel-uploads
description: "시네플로그 영화 리뷰를 올리는 사용자 유튜브 채널 UCX9JkEbYxU-W8OTB2t0-eaA — 이 크롬 계정엔 없음(스튜디오 권한 없음), 공개 목록은 yt-dlp 로 · 10-17 기준 공개 5편(01·04·13·16·17)"
metadata:
  node_type: memory
  type: reference
  originSessionId: e5e1492c-0c2f-44e7-a90c-2405ab058d81
  modified: 2026-10-17T06:21:25.275Z
---

2026-10-17 사용자: "https://studio.youtube.com/channel/UCX9JkEbYxU-W8OTB2t0-eaA/content 이채널내껀데 작업한거중에서 안올린거 영화찾아봐"

- 채널 ID `UCX9JkEbYxU-W8OTB2t0-eaA` = 시네플로그 영화 리뷰 채널.
- 이 컴퓨터 크롬(Claude in Chrome)에 로그인된 구글 계정의 채널 목록(구름이야기·야담마님·야담과 달빛이야기 등)에는 **없다** → 스튜디오는 「이 페이지를 볼 권한이 없습니다」. 로그인은 사용자 몫(비밀번호 입력 금지).
- 대신 공개 목록: `yt-dlp --cookies-from-browser firefox --flat-playlist --print "%(id)s %(duration_string)s %(title)s" https://www.youtube.com/channel/UCX9JkEbYxU-W8OTB2t0-eaA/videos` (윈도 출력은 cp949 로 읽기). 일부공개·비공개·예약은 안 보인다.
- 10-17 공개 5편을 길이로 맞춤: 01 헤즈오브스테이트(XvJTvN-yZO4 17:27) · 04 위드아웃리모스(qmcteV5lcMA 19:55) · 13 울프스(SwON_aNlO90 21:38) · 16 핀치(PZNtiPjS5Vc 27:12) · 17 그레이하운드(ZX5dZJ9srTg 19:51).
- 공개 목록에 없는 완성본: 02·03·05·06·07(+일본어판)·08·09·10·11·12·14·15·18·19·20.

- ★10-17 사용자 "이거 안걸렸어" — 내가 「옛 방식(10-14 v12 전) 편은 소유권 주장 걸릴 수 있다」고 하자 한 말. 공개 중인 13 울프스(10-09 옛 방식, 애플 영화)가 소유권 주장 없이 올라가 있다는 뜻으로 읽음 → 옛 방식이라고 무조건 걸린다고 겁주지 말 것. 걸리고 안 걸리고는 편마다 다름(17 그레이하운드 v9 는 걸렸음).

관련: [[cineflog-channel]] · [[cineflog-20-family-plan-2]]
