---
name: cineflog-01-02-remake
description: "★★시네플로그 01 헤즈 오브 스테이트·02 패밀리 플랜 다시 만들기(10-14) — v9 도구+새 prep 도구로 두 편 동시, 작업 D:/cine_work/ep01v2_헤즈오브스테이트·ep02v2_패밀리플랜, 진행 상황은 본문 끝"
metadata:
  node_type: memory
  type: project
  originSessionId: e91dc7e8-0158-4dc4-b763-6912fa14b949
  modified: 2026-10-14T09:04:00.038Z
---

2026-10-14 저녁 사용자: "다음영화할거야" → (밤파일=다운로드 폴더) "https://www.youtube.com/watch?v=hYIBdpoWibU 패밀리플랜이야" · "벤치영상보고이야기의 흐름이 자연스럽게 저작권걸리지않게 만들어줘" · "https://www.youtube.com/watch?v=0kpzwBKyLBM 헤즈오브스테이트" · "이렇게 두개만들어줘" · "로고는 화면키워".
- 이미 올라간 01·02(09-29·30 옛 방식)를 17 그레이하운드 v12 방식으로 다시. 번호는 그대로 01·02, 옛 완성본은 _옛 으로.
- 벤치: 02 = 리씨네 547만(원본 85분 전용기 함정에서 끊음 → 우리는 결말까지), 01 = 달콤 리뷰 32만(40분, 결말까지).
- 원본: C:/Users/uere/Downloads/패밀리 플랜.mkv(1920x804, AYA 로고 오른쪽 위 y17~39) · [ 헤즈 오브 스테이트 ] ….mp4(1920x1080 꽉 참, 박힌 자막 y900~1060). 패밀리 플랜 2.mkv 도 받아져 있음(아직 안 함).
- 새 도구 presets/시네플로그/v9/prep/: sm.py(Speechmatics 문장부호·화자) · scenes.py · lines_sm.py · edl.py·bench_flow.py·jev_bench.py(편 가리지 않게) · shot_desc.py(ep.json ctx) · ★dcand.py(대사 줄마다 앞뒤 깨끗한지 미리 → ✓ 줄만 고르면 plan 「말 잘림」 0) · dfix.py(대본 대사 ✓/✗+3초 간격) · dfree.py(지금 대본에 더 넣을 수 있는 ✓ 대사) · review_n.py(나레 줄 밑 그림 설명) · textscan.py(반전하면 거꾸로 보일 글자 조각 시트) · mkbatch.py.
- v9 고침: build_v9 ep.json burn(자막 자리)·logo(확대로 잘라냄)·quiet(유명 노래 구간 원본 소리 0.35배)·굽기 끝 소리 맞춤 자동 · plan_v9 대사 창도 {"noflip": True}.
- 결과(계획): 02 = 18:19·나레 40%·대사 창 318 / 01 = 17:58·나레 46%·대사 창 287. 둘 다 결말까지. 20분 정도 목표지만 억지로 안 채움.
- 01 대본은 포크 작업자가 씀(그림 보고 고친 것: 공격은 수송기+드론, 비스트 들이받은 건 소방차, 커크 정체 복선 등).
- 그림 확인으로 고친 사실: 02 고백 장소는 모텔 수영장, 킬보이 알아본 곳은 모텔 주차장, 스위트룸은 「사랑의 안개」+빨간 레이저+인질, 제시카는 장대높이뛰기가 아니라 대나무 장대 창던지기.
- 썸네일 보기(카랑 꼴, 빨간 글자): scratchpad th02/opts02.jpg(A 빨간 음료 「전설의 킬러를 건드렸다!」 B 아기 안고 마트 C 아내 목에 총구 D 레이저 E 킬러 잡는 엄마) · th01/opts01.jpg(A 불타는 에어포스원 B 격추 1초 전 C 뛰어내려 D 낙하산 찢어짐 E 헬기). ★사용자가 고르기 전.
- ✅10-14 저녁 완성: 완성본/02_패밀리플랜.mp4 18:17·-16.0 LUFS·정점 -1.4·나레 41%·대사 창 317·조각 563 · 01_헤즈오브스테이트.mp4 17:26·-16.1·-2.3·나레 45%·대사 창 284·조각 554. 관문 pre/final 0, finalcheck(빈 틈·까만·멈춤·끝 검정) 0. 캡컷 「시네플로그02v2」「시네플로그01v2」(표지는 보기 A 임시) + 완성본/*_캡컷. 업로드 txt. 옛 01·02 는 완성본/_옛/*_0929·_0930.
- ★남은 것: 썸네일 고르기(보기 D:/cine_work/ep0*v2_*/썸네일_보기_ABCDE.jpg) → 완성본 *_썸네일1·2.jpg, 캡컷 표지 바꾸기. 그다음 일부공개로 CID 확인.
- 제브 ⑨ 는 01 에서 74줄을 헛짚었다(agy 설명이 인물 이름을 틀림) → review_n 전 줄을 눈으로 보고 허용(gate_allow_why). 고친 것: 노엘 기습 컷(5:47), 제목 그래픽(8:14) 피함.

관련: [[cineflog-greyhound-next]] [[cineflog-cid-transform-all-windows]] [[cineflog-include-ending]] [[cineflog-thumbnail-red-urgent]] [[cineflog-logo-zoom]]
