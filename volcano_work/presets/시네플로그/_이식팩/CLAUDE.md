# 영화롱폼(시네플로그) — Claude 작업 지침 (2026-10-09판 · 13~19편 방식)

이 팩은 **영화 리뷰 롱폼 채널 「시네플로그」 프리셋**이다. 사용자가 "영화프리셋 불러와", "영화만들던거 불러와", "시네플로그", 또는 영화 파일 위치만 던지면 이걸로 한 편을 만든다.
사용자에게는 **한국어로만** 말한다. 묻지 말고 끝까지 만들고 결과를 보고한다("지금부터는 묻지말고 다 완성해줘").

## 0. 먼저 읽을 것 (순서대로)
1. 설치 확인: `python %USERPROFILE%\volcano_work\presets\시네플로그\check_setup.py` — `[없음]` 이 있으면 무엇이 필요한지 사용자에게 말한다.
2. `%USERPROFILE%\volcano_work\presets\시네플로그\README.md` — 맨 앞 「지금의 시네플로그」 다음, 「13편부터」「13~19편 결과」「마무리 비평」「한국 영화」「07편 G20」. 나머지는 편마다 겪은 일(문제가 생기면 찾아본다).
3. `gemini_tts\BRIEF_cine_work.md` — 한 편을 만드는 순서(1단계 대본·계획 → 2단계 굽기). ★이 팩에선 작업자 나누기 없이 혼자 다 한다.
4. `%USERPROFILE%\volcano_work\docs\영화리뷰_공부\` — 선생님(유튜브 「무비마스터」) 정규강의 1~4강 노트. 저작권·편집·썸네일 규칙의 근거.
5. `%USERPROFILE%\volcano_work\docs\시네플로그_기억\` — 사용자가 한 말을 정리한 기억 파일. 특히 `cineflog-channel.md`·`cineflog-resume-2026-09-30.md`.
6. 가장 가까운 옛 편 폴더(`ep13_울프스`~`ep19_강릉`)를 그대로 복사해서 쓴다. 새로 발명하지 말 것.
   - 한국어 자막이 그림에 박힌 외화 → ep13·15·16·17 (07편 방식 + 박힌 자막 잘라 내기)
   - 한국어 srt 가 따로 있는 외화 → ep14 (02편 방식)
   - 한국 영화 → ep19 (Groq language=ko 단어 시각 받아쓰기 + dlevel.py)

## 1. 꼭 지키는 사용자 규칙
- 원본 컷 **3초 단위**(≤2.9초, 좌우반전한 대사는 ≤3.95초), 쓴 구간끼리 원본에서 **3초 이상 띄운다**. build 가 끝에 "3초 넘는 컷 / 간격 3초 미만" 개수를 낸다 — 0 이어야 한다.
- **영상 안(나레·자막·화면 글자)에 영화 제목 금지.** 제목과 같은 낱말(사람·배·도시·가게 이름)은 다른 말로.
- **자막은 무조건 한 줄**, 약 18자(폭 1800px) 넘으면 다음 자막으로.
- **나레 → 원본 대사 1~4줄 → 나레 (티키타카).** 올나레 금지. 나레 비중 40~45%, 나레 4,300~4,800자, 완성 22~26분. 대사 소리는 나레와 같은 크기(-16 LUFS, dlevel.py).
- 끝에 **마무리 비평 70~80초**(작품 소개·주제 해석·연출·평가(칭찬 위주)·볼 곳 추천·구독 인사), 비평에도 제목 X.
- 욕설 대사는 고르지 않는다.
- 편마다 결과물: `NN_제목.mp4` · `_썸네일1·2.jpg` · `_업로드.txt` · `_캡컷\`. **완성본만** 건네고 중간 파일 목록은 늘어놓지 않는다.

## 2. 나레 = 제미나이 TTS 목소리 Ludo (유료 TTS 쓰지 않는다)
- 크롬의 AI 스튜디오 「Generate speech」(울트라 구독 구글 계정), 목소리 **Ludo**. 1,200자씩 묶어(`mkbatch.py 1200` → batches.json) 생성.
- 도구 `gemini_tts\`: `recv.py`(127.0.0.1:8771 수신기) → AI 스튜디오 탭에 `page.js` 코드를 넣어 `cineLoop()` → 작업 폴더 `epNN\gem\bKK_*.wav` → `splitwatch.py` 가 `gem_split.py` 로 `narr\nNNN.wav·json` 으로 자른다(Groq 단어 시각). 편 폴더에 빈 `READY` 파일이 있어야 녹음이 시작된다. READY 뒤엔 나레 글을 바꾸지 말 것.
- 크롬 창이 숨겨지면 녹음 탭 타이머가 멈춘다 → 몇 분마다 스크린샷으로 깨운다. 실측 Ludo ≈ 520~540자/분.
- 막히면 사용자 허락 아래 ElevenLabs Minjun(`tts02.py`, 키 `~\.volcano\keys\elevenlabs`).

## 3. 자막·화면 (mp4)
- N(나레) GyeonggiTitle 84 기울임 · D(대사) Stylish 88 기울임 · 흰+검은 테두리 4 · 한 줄 · 로고 CINEFLOG(Noto Sans KR Black 104 회색) 오른쪽 위. 글꼴은 build 가 Windows 글꼴 폴더에서 작업 폴더 `fonts\` 로 복사한다.
- 자막 줄의 끝<=시작이 하나라도 있으면 libass 가 로고까지 안 그린다 → 고친다. 박힌 자막이 높으면 그 구간만 크게 확대(16·18편 VF 둘).
- 끝: 마지막 나레 4조각부터 BGM(`~\volcano_work\달빛롱폼\bgm\Despair and Triumph.mp3`, Kevin MacLeod CC BY 4.0 — 설명란 표기) → 검은 화면 18초.

## 4. 썸네일 (「썸네일이 90%」)
- `thumb_horror.make(src, 초, out, 아래말, 위말, font=T.DOHYEON, sl=0.2, maxsz=300, gsz=110, bright=1.2~1.45)` — 아래 아주 큰 빨강(도현체, 눕힘)·위 초록 한마디. 밝고 센 장면(폭발·피·괴로운 얼굴·총), 어두운 장면 금지. 장면 초를 노트에 적는다.
- 문구는 내가 찾는다: 같은 영화 남의 썸네일 + 같은 장르 인기 썸네일(yt-dlp `--cookies-from-browser firefox`). 줄거리 말고 후킹 문구("X나 재미있음", "너희들은 이제 X졌어"). 모음 `docs\영화리뷰_공부\썸네일분석_2026-10-03\분석.md`.

## 5. 캡컷
- `capcutNN.py`(옛 편 복사) → `capcut_style04.py <드래프트>`(사용자가 맞춘 04편 꼴, `시네플로그04_꼴.json`) → `capcut_to_final.py 시네플로그NN NN_제목` 으로 완성본 `_캡컷` 폴더.
- 캡컷이 켜져 있으면 드래프트를 고치지 않는다. 캡컷 목록이 텅 비면 README 「캡컷 목록이 텅 빌 때」.
- 사용자에게 명령어를 치라고 하지 않는다 → 필요하면 바탕화면 더블클릭 bat(ASCII·CRLF)로 준다.

## 6. 경로 (설치.bat 이 맞춘다)
- 도구 `%USERPROFILE%\volcano_work\presets\시네플로그\` · 완성본 `%USERPROFILE%\volcano_work\시네플로그\완성본\` · 원본 `%USERPROFILE%\volcano_work\시네플로그\영화원본\`(또는 사용자가 알려 준 곳 — 웹하드 다운로드 폴더 아래 깊게 find)
- 작업 폴더 `D:\cine_work\epNN_이름\`(D 드라이브가 없으면 `%USERPROFILE%\cine_work`, 환경변수 CINE_WORK 로 바꿀 수 있음). 녹음 도구는 `<작업폴더>\tts\`.
- 캡컷 드래프트 `D:\다운로드\CapCut Drafts\`(틀 `0826 (2)`·`0826 (8)`).
- 키(확장자 없는 파일, 키 한 줄): `%USERPROFILE%\.volcano\keys\groq`(받아쓰기 — 필수) · `elevenlabs`(예비). 이 팩엔 키가 없다.
- 파일명에 이상한 글자가 있으면 ffmpeg 가 "Illegal byte sequence" → `ffmpeg -i 원본 -map 0:v:0 -map 0:a:0 -c copy src.mp4` 로 작업 폴더에 복사.

## 7. 작업 기록
- 사용자 지시는 원문 그대로 README 에 박제하고, 편이 끝나면 README 와 `docs\시네플로그_기억\cineflog-resume-2026-09-30.md` 를 고친다.
- 일본어판(VOICEVOX)은 `일본어판\README.md` — VOICEVOX 를 따로 설치해야 한다.
