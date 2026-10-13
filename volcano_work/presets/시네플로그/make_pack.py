# -*- coding: utf-8 -*-
"""시네플로그 프리셋 이식팩 만들기 → ~/영화롱폼_이식팩(폴더) + ~/영화롱폼_이식팩.zip
도구를 크게 고치면 다시 돈다. 옛 팩은 _옛판_<날짜> 로 이름만 바꿔 둔다(지우지 않음).
틀 문서: _이식팩/(CLAUDE.md · README.md · install.ps1 · 설치.bat)
"""
import glob, os, shutil, time, zipfile
H = os.path.expanduser("~")
HERE = os.path.dirname(os.path.abspath(__file__))
V = f"{H}/volcano_work"
OUT = f"{H}/영화롱폼_이식팩"
T = os.path.join(HERE, "_이식팩")
FONTDIRS = [f"{H}/AppData/Local/Microsoft/Windows/Fonts", os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts"),
            f"{V}/fonts", "D:/cine_work/ep19_강릉/fonts"]
FONTS = ["GyeonggiTitleB.ttf", "Stylish.ttf", "NotoSansKR-Black.ttf", "Pretendard-Black.otf", "Pretendard-Bold.otf",
         "DoHyeon-Regular.ttf", "Jalnan2TTF.ttf", "Recipekorea 레코체 FONT.ttf"]
BGM = ["Despair and Triumph.mp3", "Healing.mp3"]
MEMORY = ["cineflog-channel", "cineflog-resume-2026-09-30", "cineflog-japanese-version", "movie-review-study",
          "longform-tts-gemini", "drama-binge-preset", "longform-thumbnail-emotion-curiosity", "bench-copy-everything",
          "answer-in-korean", "dont-ask-just-do", "deliver-only-the-final-video", "no-work-files-only-final",
          "say-done-immediately", "log-every-user-instruction", "always-commit-session-record", "irreversible-check-first",
          "file-deletion-blocked-use-bat", "youtube-download-firefox-cookies", "flow-via-claude-in-chrome",
          "lecture-applied-2026-10-08"]
MEMDIR = f"{H}/.claude/projects/C--Users-uere/memory"
SKIP_DIRS = {"__pycache__", "_이식팩", "clips", "blocks", "narr", "gem", "asr", "chk", "fonts"}
SKIP_EXT = {".mp4", ".mkv", ".wav", ".mp3", ".m4a", ".aac", ".jpg", ".png", ".log"}

def tree(src, dst):
    n = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1].lower() in SKIP_EXT and "썸네일분석" not in root and "원문" not in root: continue
            s = os.path.join(root, f)
            if os.path.getsize(s) > 30_000_000: continue
            d = os.path.join(dst, os.path.relpath(s, src)); os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d); n += 1
    return n

stamp = time.strftime("%m%d")
for old in (OUT, OUT + ".zip"):
    if os.path.exists(old):
        base, ext = os.path.splitext(old) if old.endswith(".zip") else (old, "")
        os.replace(old, f"{base}_옛판_{stamp}_{time.strftime('%H%M%S')}{ext}")
os.makedirs(OUT)
print("도구", tree(HERE, f"{OUT}/시네플로그"))
shutil.copy2(os.path.join(HERE, "check_setup.py"), f"{OUT}/시네플로그/check_setup.py")
print("강의 노트", tree(f"{V}/docs/영화리뷰_공부", f"{OUT}/docs/영화리뷰_공부"))
os.makedirs(f"{OUT}/docs/기억")
for m in MEMORY:
    p = f"{MEMDIR}/{m}.md"
    if os.path.exists(p): shutil.copy2(p, f"{OUT}/docs/기억/")
    else: print("  기억 없음:", m)
os.makedirs(f"{OUT}/fonts"); os.makedirs(f"{OUT}/bgm")
for f in FONTS:
    s = next((f"{d}/{f}" for d in FONTDIRS if os.path.exists(f"{d}/{f}")), None)
    if s: shutil.copy2(s, f"{OUT}/fonts/")
    else: print("  글꼴 없음:", f)
for b in BGM: shutil.copy2(f"{V}/달빛롱폼/bgm/{b}", f"{OUT}/bgm/")
# 캡컷 틀: 캡컷 폴더의 원본 틀(설정 파일만) — 없으면 옛 팩 것
cc = "D:/다운로드/CapCut Drafts"
oldpack = sorted(glob.glob(f"{H}/영화롱폼_이식팩_옛판_*/캡컷틀"))
for t in ("0826 (2)", "0826 (8)"):
    src = oldpack[-1] + "/" + t if oldpack else f"{cc}/{t}"
    shutil.copytree(src, f"{OUT}/캡컷틀/{t}", ignore=shutil.ignore_patterns("*.mp4", "*.mp3", "*.wav", "crypto_key_store.dat", "draft.extra"))
for f in ("CLAUDE.md", "README.md"): shutil.copy2(os.path.join(T, f), OUT)
ps = open(os.path.join(T, "install.ps1"), encoding="utf-8-sig").read()
open(f"{OUT}/install.ps1", "w", encoding="utf-8-sig", newline="\r\n").write(ps)          # PowerShell 5.1 은 BOM 이 있어야 한글을 읽는다
bat = ('@echo off\r\ncd /d "%~dp0"\r\nwhere python >nul 2>nul\r\nif errorlevel 1 (\r\n'
       '  echo Python is not installed. Install Python 3.10+ from https://www.python.org  [check "Add python.exe to PATH"]\r\n'
       '  pause\r\n  exit /b\r\n)\r\npowershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"\r\npause\r\n')
open(f"{OUT}/설치.bat", "w", encoding="ascii", newline="").write(bat)
with zipfile.ZipFile(OUT + ".zip", "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(OUT):
        for f in files:
            s = os.path.join(root, f); z.write(s, os.path.join("영화롱폼_이식팩", os.path.relpath(s, OUT)))
nf = sum(len(f) for _, _, f in os.walk(OUT))
print("완성", OUT + ".zip", round(os.path.getsize(OUT + ".zip") / 1e6, 1), "MB", nf, "파일")
