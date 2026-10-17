# 시네플로그 프리셋 — 영화 리뷰 롱폼(벤치 흐름 따라 · 강의 3초 규칙 · 우리 나레)

유튜브 「시네플로그」 채널의 영화 리뷰 롱폼(25분 이상)을 만드는 도구·규칙·기억 묶음. 영상·녹음·원본 영화·API 키는 넣지 않았다.

## 설치 (다른 컴퓨터)
1. `설치.bat` 더블클릭 → `%USERPROFILE%\volcano_work` 와 Claude 기억 폴더에 복사.
2. `%USERPROFILE%\.volcano\keys\` 에 열쇠 파일(speechmatics · groq · typesafe). 값은 어디에도 적지 않는다.
3. `volcano_work` 에서 Claude Code 를 켜고 "시네플로그 불러와".
4. 자막 글꼴: 새 편 작업 폴더(`D:/cine_work/epNN_제목/fonts/`)에 `volcano_work/fonts/시네플로그_자막/` 을 통째로 복사(나레 카페24 당당해 · 대사 광화문=Yeonil_TM · 지무비식 강조 글꼴들).

## 먼저 읽을 곳 (2026-10-17 판)
- `volcano_work/presets/시네플로그/README.md` 맨 앞부터: 「★★★★가장 기본」(나레 밑엔 그 장면 · 결말까지 · ★25분 이상) → 「★유튜브 채널·올린 편」 → 「둥둥아빠 강의 체크리스트」 → 「★★★새 편 순서」(v9 + prep 도구, 처음부터 한 번에).
- ★지금 방식 = `presets/시네플로그/v9/` + `v9/prep/`:
  준비(`prep/sm.py`·`scenes.py`·`fp.py`·`black_map.py` → `lines_sm.py`·`match.py`·`edl.py`·`jev_bench.py`·`bench_flow.py`·`shot_desc.py`·`dcand.py`)
  → 대본 `script.py`(줄마다 그 장면 원본 구간, 대사는 dcand ✓ 줄만) → `plan_v9.py --dry` → `review_n.py`(나레 밑 그림으로 사실 확인)
  → 녹음(AI 스튜디오 Ludo, `gemini_tts/`) → `plan_v9.py` → `narr_pic.py` → ★`prep/flipsheet.py`(반전 조각 전부 뒤집어 보고 거꾸로 글자 줄 noflip, **cut 전에**)
  → `build_v9.py cut` → `build_v9.py`(관문 final · -16 LUFS) → `prep/finalcheck.py`
  → 캡컷 `capcut_v9.py`(CC_NAME) → `v9/capfix.py` → `capcut_style04.py` → `capcut_font.py`(지무비식 자막) → `capcut_to_final.py`
  → 썸네일 보기 5장(`thumb_quote.py`) → `thumb_deliver.py` 로 완성본 영상 옆에 → 사용자가 고르면 `thumb_deliver.py --pick`.
- 편 예시: `presets/시네플로그/ep20_패밀리플랜2/`(10-17, 25:47) · `ep04v2_위드아웃리모스/`(지무비식 자막 첫 편) · `ep17v2_그레이하운드/`(3초 규칙 v12).
- 강의 공부: `volcano_work/docs/영화리뷰_공부/` · 규칙 모음 `volcano_work/docs/PLAYBOOK.md` 「리뷰 롱폼 소유권 주장(CID)」 절.
- 기억: `_claude_memory/` — ★narration-matches-picture-basic · cineflog-cid-transform-all-windows · cineflog-include-ending · cineflog-min-20min(25분 이상) · preset-style-means-full-caption-look · thumbnail-options-next-to-final · cineflog-youtube-channel-uploads · talk-before-making.

## 지금 상태 (2026-10-17)
- 완성본 20편(01~20, 07 일본어판 포함). 01·02·04·03 은 3초 규칙(v9) 방식으로 다시 만듦(03 은 10-17, 25:34). ★옛 방식 편(05~12·14·15·18·19)은 "다 엉망" — 올리지 말고 하나씩 다시 만든다(README 「옛 편 다시 만들기」).
- 20 패밀리 플랜 2 완성(25:47·-16 LUFS·관문 0·finalcheck 0·글자 거꾸로 40줄 noflip·캡컷 「시네플로그20」) · 03 아이 돈 언더스탠드 유 다시(25:34·나레 40%·캡컷 「시네플로그03v2」). 둘 다 썸네일 보기 A~E 사용자 고르기 전.
- 채널(UCX9JkEbYxU-W8OTB2t0-eaA) 공개 5편: 01·04·13·16·17. 새 방식으로 올릴 수 있는 것: 02v2·03v2·20(썸네일 고르기 전). 옛 방식 편은 사용자 "저거 다 엉망이야 다시만들어야해" — 올리지 않고 다시 만든다(13 울프스는 옛 방식인데 소유권 주장은 안 걸렸음, "이거 안걸렸어").
- 다음 편: 대본 쓸 때부터 대사는 3초 안 ✓ 줄만 · 결말까지 · **25분 이상** · 지무비식 자막(capstyle jimovie) · 썸네일은 같은 영화 인기 썸네일부터 보고 보기 5장.
