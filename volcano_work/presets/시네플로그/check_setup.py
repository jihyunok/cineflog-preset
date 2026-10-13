# -*- coding: utf-8 -*-
"""시네플로그 설치 확인 - 설치.bat 이 부르고, Claude 도 작업 전에 돈다. 없는 것을 한국어로 알려 준다."""
import os, shutil, subprocess, sys
ok = True
def say(b, m):
    global ok; ok &= bool(b); print(("  [됨]  " if b else "  [없음] ") + m)
H = os.path.expanduser("~")
P = f"{H}/volcano_work/presets/시네플로그"
W = os.environ.get("CINE_WORK") or ("D:/cine_work" if os.path.isdir("D:/") else f"{H}/cine_work")
print("\n영화롱폼(시네플로그) 설치 확인\n")
say(sys.version_info >= (3, 10), f"파이썬 3.10 이상 (지금 {sys.version.split()[0]})")
for mod, pip in (("PIL", "pillow"), ("numpy", "numpy")):
    try: __import__(mod); say(True, pip)
    except ImportError: say(False, f"{pip} - pip install {pip}")
say(bool(shutil.which("yt-dlp")) or subprocess.run([sys.executable, "-m", "yt_dlp", "--version"], capture_output=True).returncode == 0, "yt-dlp")
ff = shutil.which("ffmpeg")
say(bool(ff), "ffmpeg - 없으면 명령창에서: winget install Gyan.FFmpeg  (설치 후 창을 새로 열기)")
if ff:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    say(" ass " in out and " subtitles " in out, "ffmpeg 에 자막(ass·subtitles) 필터")
say(os.path.exists(f"{P}/README.md"), "도구 → volcano_work/presets/시네플로그")
say(os.path.exists(f"{H}/volcano_work/docs/영화리뷰_공부/4강_요약_정리.md"), "강의 노트 → volcano_work/docs/영화리뷰_공부")
say(os.path.exists(f"{H}/volcano_work/달빛롱폼/bgm/Despair and Triumph.mp3"), "끝 음악 → volcano_work/달빛롱폼/bgm")
say(os.path.exists(f"{W}/tts/recv.py"), f"제미나이 녹음 도구 → {W}/tts")
fds = [os.path.join(os.environ.get("LOCALAPPDATA", f"{H}/AppData/Local"), "Microsoft/Windows/Fonts"), os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts")]
for f in ("GyeonggiTitleB.ttf", "Stylish.ttf", "NotoSansKR-Black.ttf", "Pretendard-Black.otf", "Pretendard-Bold.otf"):
    say(any(os.path.exists(f"{d}/{f}") for d in fds), f"글꼴 {f}")
say(os.path.exists(f"{H}/volcano_work/fonts/DoHyeon-Regular.ttf"), "글꼴 도현체 → volcano_work/fonts (썸네일)")
say(os.path.exists("D:/다운로드/CapCut Drafts/0826 (2)/draft_content.json"), "캡컷 틀 → D:/다운로드/CapCut Drafts/0826 (2)  (캡컷 프로젝트 위치도 이 폴더로)")
kd = f"{H}/.volcano/keys"; os.makedirs(kd, exist_ok=True)
say(os.path.exists(os.path.join(kd, "groq")), "Groq API 키 (받아쓰기·나레 자르기) → " + os.path.normpath(os.path.join(kd, "groq")) + "  (확장자 없는 파일에 키 한 줄)")
print("  [참고] 나레는 크롬 AI 스튜디오(제미나이 TTS, 목소리 Ludo) - 구글 계정 로그인만 있으면 된다. ElevenLabs 키(elevenlabs)는 예비.")
print("\n" + ("모두 준비됐어요." if ok else "[없음] 을 채우고 설치.bat 을 다시 실행하세요.") + "\n")
