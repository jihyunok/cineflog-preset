---
name: cineflog-04-without-remorse-remake
description: "★★시네플로그 04 위드아웃 리모스 다시 만들기(10-16) — 영화리뷰롱폼 엔진은 6분이 끝이라 사용자 \"시네플로그로 20분 만들어줘\", v12 방식 · D:/cine_work/ep04v2_위드아웃리모스 · 진행은 본문 끝"
metadata:
  node_type: memory
  type: project
  originSessionId: 341d4b93-855c-4e6d-8902-a137da5ac392
  modified: 2026-10-16T12:01:59.271Z
---

2026-10-16 사용자: "6분이라고?" → "완성이 6분이야?" → "시네플로그로 20분 만들어줘".
- 배경: [[movie-review-longform-preset]] 엔진으로는 이 영화가 완성 6분(362초)이 최대(10분 요청도 12단계 5번 반려). 그래서 시네플로그(우리 도구)로.
- 04편은 10-01 옛 방식(24:49, 나레 42%)으로 이미 있다 → [[cineflog-01-02-remake]] 처럼 v12 방식(3초 규칙·결말까지·CID 안전, [[cineflog-cid-transform-all-windows]])으로 다시, 번호 04 그대로, 옛 완성본은 완성본/_옛.
- 원본: C:/Users/uere/Downloads/Tom.Clancys.Without.Remorse.2021.1080p.x264.mkv → 작업 폴더 src.mp4(v:0 + a:1 영어, 1920x800 → ep.json h 800) · ko.srt(공식 한국어 자막 트랙 26) · en.srt.
- 벤치: 씨겐 See You Again BNHbTGhkgmM (20:40, 155만, bench_y 138). 447만짜리 SAfGpxJUAB0 는 개봉 전(2021-03) 다른 영화라 뺐다.
- 준비: prep1(sm·scenes·fp·black_map) → prep2.sh(shot_desc·lines_sm·match·edl·jev_bench·bench_flow·dcand) 자동 연결.

**Why:** 사용자는 영화 리뷰를 20분 정도로 원한다([[cineflog-min-20min]]), 볼케이노 엔진은 액션 영화에서 짧게 막힌다.
**How to apply:** 대본은 [[narration-matches-picture-basic]]·[[apply-lecture-rules-cineflog]]·[[cineflog-include-ending]] 그대로, 굽기 전 관문 0, 썸네일은 [[cineflog-thumbnail-red-urgent]] 보기 → 사용자 고름.

★글꼴: 사용자 "글자체들은 원래프리셋대로해줘" → "시네플로그말고" = **영화리뷰롱폼 프리셋 글꼴**. 나레 카페24당당해(사용설명서 「자막 글꼴」) · 대사 광화문(엔진 대사 역할 서체 = 이 컴퓨터 Yeonil_TM) · 바로 세움. build_v9 에 ep.json `nfont`·`dfont` 를 새로 받게 했다(없으면 종전 꼴). 작업 폴더 fonts/ 에 두 파일. 캡컷 꼴(capcut_style04)도 이 글꼴로 바꿔야 한다.

진행: 10-16 17:40 준비 시작 → 컷 문턱 0.28 이 406컷뿐(어두운 영화) → 0.12 로 969컷 다시(prep3) · shot_desc 2,056 · dcand ✓1,376 · ko_ref.py → lines_ko.txt(공식 한국어 자막 참고표). 18:20쯤 대본은 포크 작업자에게(items·batches 까지, READY·녹음은 메인).
10-16 저녁: 녹음 135줄(AI 스튜디오 98 Ludo, 5묶음, 증상 0) → 실제 17:54 → "20분" 이라 N 그대로 A 42·D 1 더해 19:52 → 제브 ⑨ 43 눈으로(진짜 5곳 고침) → 1판 굽기 19:54·-16.1 → 완성 검사에서 견인차 글씨 거꾸로·까만 계단 조각 발견 → 반전 조각 552개 전수 시트로 글자 12줄 noflip(ICU 표지는 원본이 거울상이라 되돌림) → ✅4판 완성 19:54·-16.2 LUFS·정점 -2.3, finalcheck 빈 소리·멈춤·끝 검정 0(어두운 7곳은 얼굴 보이는 밤 장면).
완성본/04_위드아웃리모스.mp4 · _업로드.txt · _캡컷(「시네플로그04v2」, 자막 프리셋 글꼴, 표지 보기 A 임시) · 옛 10-01 판은 완성본/_옛/*_1001. 사본 presets/시네플로그/ep04v2_위드아웃리모스/.
★10-16 밤 사용자 "글자가 내가새로준 지침에 보면 큰글자도있고 색깔있는글자도 있고 다양한데 넌 그걸안지켰네?" → 글꼴 이름만 바꾼 게 틀림. 지무비식 자막(capstyle=jimovie · emph.json 97줄 · v9/jm_style.py) 넣고 5판 다시 구움 19:54·-16.2, 관문 0 → 완성본 교체 · 캡컷도 글자 구간마다 글꼴·색(801구간, 깐 글꼴 경로).
**How to apply:** "프리셋대로" 는 글꼴 이름이 아니라 그 프리셋 자막 꼴 전부(크기 단계·강조 색·감정 글꼴). [[movie-review-longform-preset]]
★썸네일은 10-16 새 기본 꼴(thumb_quote)로 보기 다시 5장: D:/cine_work/ep04v2_위드아웃리모스/썸네일_보기2_ABCDE.jpg (A 2117 차 안 노려봄 · B 2140.5 다그침 · C 3187 수송기 소리침 · D 2303 교도소 · E 2145) — 옛 karang 보기는 썸네일_보기_ABCDE.jpg.
★10-17 사용자 "잘만들었어 그런데 섬네일은 왜 같은 파일안에 안넣니 찾기힘들어" → 보기 A~E·한눈에(A~E 글자)를 완성본/04_위드아웃리모스_썸네일보기_* 로 넣음([[thumbnail-options-next-to-final]]).
★남은 것: 썸네일 고르기 → `python presets/시네플로그/thumb_deliver.py --pick 04_위드아웃리모스 X [Y]` → 캡컷 표지(작업 폴더 thumb_A.jpg 바꾸고 draft_cover). 그다음 일부공개로 CID 확인.
썸네일 보기 5장 D:/cine_work/ep04v2_위드아웃리모스/썸네일_보기_ABCDE.jpg (A 2096 불타는 차 · B 2570 감옥 · C 3187 수송기 · D 5052 방독면 · E AI 크렘린) — 사용자 고르기 전.
