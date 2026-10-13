# 시네플로그 프리셋 — 영화 리뷰 롱폼(벤치 흐름 따라 · 강의 3초 규칙 · 우리 나레)

유튜브 「시네플로그」 채널의 영화 리뷰 롱폼(약 27분)을 만드는 도구·규칙·기억 묶음. 영상·녹음·원본 영화·API 키는 넣지 않았다.

## 설치 (다른 컴퓨터)
1. `설치.bat` 더블클릭 → `%USERPROFILE%\volcano_work` 와 Claude 기억 폴더에 복사.
2. `%USERPROFILE%\.volcano\keys\` 에 열쇠 파일(speechmatics · groq · typesafe). 값은 어디에도 적지 않는다.
3. `volcano_work` 에서 Claude Code 를 켜고 "시네플로그 불러와".

## 먼저 읽을 곳
- `volcano_work/presets/시네플로그/README.md` 맨 앞 「★★★다음」 → 「16 핀치 v5」~「v8」(지금 방식, 16 핀치 v8 은 소유권 주장 없이 올라감).
- 도구: `volcano_work/presets/시네플로그/ep16v5_핀치/` — fp·match·edl(벤치 편집표) → plan_v8 → fix3~fix10 → build_v8 → check_all·subcheck4·narr_frag·narr_check(제브) → capcut_v8.
- 나레 녹음·자르기: `presets/시네플로그/gemini_tts/` (gem_split → narr_recut → realign).
- 강의 공부: `volcano_work/docs/영화리뷰_공부/` (원문 PDF 는 뺌). 제브(글 판정): `volcano_work/_제브/CLAUDE.md`.
- 기억: `_claude_memory/` — ★cineflog-greyhound-next(다음 할 일) · follow-bench-picture-no-own-picks · narration-split-fragments-no-freeze · dungdung-lecture-checklist.

## 다음 할 일 (2026-10-13)
17 그레이하운드를 핀치 v8 방식으로(벤치 https://www.youtube.com/watch?v=I9Jx9Co8kWs). 먼저 도구 세팅: gem_split 경계를 소리 크기로 · 대사 컷 가장자리를 실제 말 끝으로 · 굽기 직전 관문(나레 토막·대사 잘림·멈춤·까만 화면·자막 시각). 받아쓰기는 Speechmatics. 원본 영화 파일은 따로 받아야 한다.
