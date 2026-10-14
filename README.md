# 시네플로그 프리셋 — 영화 리뷰 롱폼(벤치 흐름 따라 · 강의 3초 규칙 · 우리 나레)

유튜브 「시네플로그」 채널의 영화 리뷰 롱폼(약 27분)을 만드는 도구·규칙·기억 묶음. 영상·녹음·원본 영화·API 키는 넣지 않았다.

## 설치 (다른 컴퓨터)
1. `설치.bat` 더블클릭 → `%USERPROFILE%\volcano_work` 와 Claude 기억 폴더에 복사.
2. `%USERPROFILE%\.volcano\keys\` 에 열쇠 파일(speechmatics · groq · typesafe). 값은 어디에도 적지 않는다.
3. `volcano_work` 에서 Claude Code 를 켜고 "시네플로그 불러와".

## 먼저 읽을 곳 (2026-10-14 판)
- `volcano_work/presets/시네플로그/README.md` 맨 앞 「★★★★가장 기본」(나레 밑엔 그 장면 · ★결말까지 · 20분 정도) → 「★17 그레이하운드 v9」 절 끝까지(v10~v12: 소유권 주장 대응·결말·끝 검은 화면).
- ★지금 방식 = `presets/시네플로그/v9/`: `plan_v9.py`(대본 줄마다 그 장면 구간에서만 3초 조각 · 대사 창도 처음부터 1.05배·화면 3초 안) → `narr_pic.py`(제브 나레↔그림) → `gate.py pre`(⑫ 원본 3초 넘는 조각 실패 · ⑬ 20분 알림) → `build_v9.py cut` → `build_v9.py`(gate final, 끝 검은 화면 없음) → `capcut_v9.py` → `capfix.py` → `../capcut_style04.py` → `../capcut_to_final.py`. 대본을 고치면 `renum.py`(글 기준 녹음 번호 옮기기).
- 편 예시: `presets/시네플로그/ep17v2_그레이하운드/script.py`(v12 최종 대본, `at()`·결말 절) · `gate_allow_why.txt`(허용 이유).
- 썸네일: `presets/시네플로그/thumb_karang.py`(빨간 굵은 비스듬 글자 + 급박한 장면 문장).
- 나레 녹음: `presets/시네플로그/gemini_tts/`(AI 스튜디오 98 계정 Ludo · page.js · recv.py · gem_split).
- 강의 공부: `volcano_work/docs/영화리뷰_공부/` · 규칙 모음 `volcano_work/docs/PLAYBOOK.md` 「리뷰 롱폼 소유권 주장(CID)」 절.
- 기억: `_claude_memory/` — ★cineflog-cid-transform-all-windows(3초 규칙으로 소유권 주장 통과) · cineflog-include-ending · cineflog-min-20min · cineflog-no-black-tail · cineflog-thumbnail-red-urgent · narration-matches-picture-basic · talk-before-making.

## 지금 상태 (2026-10-14)
- 17 그레이하운드 v12 완성(19:50, 결말까지): 원본 조각을 대사 창 포함 모두 화면 3초 안으로 바꿔 **Apple 소유권 주장 안 뜸**(반전·확대·색조만 센 v10 은 걸렸음). 끝 음원 15초 검은 화면은 뺌.
- 다음 편: 대본 쓸 때부터 대사는 3초 안 줄만 · 결말까지 · 20분 정도(억지로 맞추지 않음) · 썸네일은 같은 영화 인기 썸네일부터 보고 빨간 글자 보기 여러 장.
