# 영화롱폼(시네플로그) 프리셋 이식팩 — 다른 컴퓨터에서 쓰기 (2026-10-09판)

13~19편을 만든 지금 방식(제미나이 Ludo 나레 · 큰 한 줄 자막 · 도현체 썸네일 · 캡컷 04꼴 · 끝 비평)을 그대로 옮긴다.

## 처음 한 번
1. 이 zip 을 아무 데나 풀고 **설치.bat** 더블클릭. 하는 일:
   - 파이썬 부품(Pillow·numpy·yt-dlp) 설치
   - 도구 → `%USERPROFILE%\volcano_work\presets\시네플로그\` · 강의 노트 → `volcano_work\docs\영화리뷰_공부\` · 기억 → `volcano_work\docs\시네플로그_기억\`
   - 끝 음악 → `volcano_work\달빛롱폼\bgm\` · 도현체 → `volcano_work\fonts\`
   - 작업 폴더 `D:\cine_work`(D 가 없으면 `%USERPROFILE%\cine_work`)와 제미나이 녹음 도구 `...\tts\`
   - 캡컷 틀 `0826 (2)`·`0826 (8)` → `D:\다운로드\CapCut Drafts\`
   - 글꼴(경기천년제목B·Stylish·Noto Sans KR Black·Pretendard·잘난체·레코체) 내 계정용 설치
   - `%USERPROFILE%\.claude\CLAUDE.md` 에 「영화프리셋 불러와 → 이 지침」 한 단락 추가(이미 있으면 그대로) → 어느 폴더에서 Claude Code 를 켜도 알아듣는다
   - 빠진 것을 한국어로 알려 주고, 키 폴더를 연다
2. 파이썬이 없으면 https://www.python.org 에서 3.10 이상("Add python.exe to PATH" 체크). ffmpeg 가 없으면 명령창에 `winget install Gyan.FFmpeg` → 창을 새로 열고 설치.bat 다시.
3. 열리는 `%USERPROFILE%\.volcano\keys` 폴더에 키 파일(확장자 없음, 키 한 줄): **`groq`**(받아쓰기 — 필수) · `elevenlabs`(예비 나레, 없어도 됨).
4. 크롬에 **Claude in Chrome** 확장 + AI 스튜디오(aistudio.google.com)에 구글 계정 로그인 — 나레를 거기서 녹음한다.
5. 캡컷: 프로젝트 위치를 `D:\다운로드\CapCut Drafts` 로. 캡컷 자막 글꼴 경기천년제목B·나다스탈리크는 캡컷 글꼴이라 캡컷에서 한 번 열면 받아진다.

## 쓰는 법 (Claude Code)
**"영화프리셋 불러와"** 또는 **"이 영화로 20편 만들어줘 (파일 위치)"**. Claude 는 `volcano_work\CLAUDE-시네플로그.md` → 도구 README → 기억 순서로 읽는다.

## 들어 있는 것
- `시네플로그\` 도구 전부 + 01~19편 대본·계획·빌더(epNN_*), `gemini_tts\`(녹음 수신기·자르기·브라우저 코드), `일본어판\`(VOICEVOX 따로 설치 필요).
- `docs\영화리뷰_공부\` 무비마스터 정규강의 1~4강 노트·원문·작품 후보·썸네일 분석. `docs\기억\` 사용자가 한 말을 정리한 기억 파일.
- `캡컷틀\` 캡컷 드래프트 틀 · `fonts\` 글꼴 · `bgm\` 끝 음악(Kevin MacLeod, CC BY 4.0).
- **영상·나레·완성본·키·로그인은 없다.** 다시 만들 땐 이 컴퓨터에서 `python %USERPROFILE%\volcano_work\presets\시네플로그\make_pack.py`.
