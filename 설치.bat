@echo off
rem Cineflog preset installer: copies volcano_work and Claude memory into this PC
setlocal
set SRC=%~dp0
robocopy "%SRC%volcano_work" "%USERPROFILE%\volcano_work" /E /NFL /NDL /NJH /NJS
set MEM=%USERPROFILE%\.claude\projects\C--Users-%USERNAME%\memory
if not exist "%MEM%" mkdir "%MEM%"
robocopy "%SRC%_claude_memory" "%MEM%" /E /XF MEMORY.md /NFL /NDL /NJH /NJS
if not exist "%MEM%\MEMORY.md" copy "%SRC%_claude_memory\MEMORY.md" "%MEM%\MEMORY.md"
if not exist "%USERPROFILE%\.volcano\keys" mkdir "%USERPROFILE%\.volcano\keys"
if not exist "D:\cine_work" mkdir "D:\cine_work"
echo.
echo Done. Put API keys into %USERPROFILE%\.volcano\keys (speechmatics, groq, typesafe).
echo Fonts: volcano_work\fonts (copy to the episode work folder fonts\ when building).
echo Then open Claude Code in %USERPROFILE%\volcano_work and say: 시네플로그 불러와
pause
