$ErrorActionPreference = "Continue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$H = $env:USERPROFILE
$V = "$H\volcano_work"
Write-Host "`n영화롱폼(시네플로그) 프리셋 설치`n"
python -m pip install --upgrade pillow numpy yt-dlp

# 도구 · 강의 노트 · 기억 · 지침
$p = "$V\presets\시네플로그"; New-Item -ItemType Directory -Force $p | Out-Null
Copy-Item "$here\시네플로그\*" $p -Recurse -Force
$d = "$V\docs\영화리뷰_공부"; New-Item -ItemType Directory -Force $d | Out-Null
Copy-Item "$here\docs\영화리뷰_공부\*" $d -Recurse -Force
$m = "$V\docs\시네플로그_기억"; New-Item -ItemType Directory -Force $m | Out-Null
Copy-Item "$here\docs\기억\*" $m -Recurse -Force
Copy-Item "$here\CLAUDE.md" "$V\CLAUDE-시네플로그.md" -Force
foreach ($x in @("시네플로그\완성본", "시네플로그\영화원본", "달빛롱폼\bgm", "fonts")) { New-Item -ItemType Directory -Force "$V\$x" | Out-Null }
Copy-Item "$here\bgm\*" "$V\달빛롱폼\bgm" -Force
Copy-Item "$here\fonts\DoHyeon-Regular.ttf" "$V\fonts" -Force

# Claude 전역 지침에 한 단락 (이미 있으면 그대로)
$gc = "$H\.claude\CLAUDE.md"; New-Item -ItemType Directory -Force "$H\.claude" | Out-Null
$mark = "# 시네플로그 영화롱폼 프리셋"
$has = (Test-Path $gc) -and ((Get-Content $gc -Raw -Encoding UTF8) -like "*$mark*")
if (-not $has) {
  $txt = "`r`n$mark`r`n- `"영화프리셋 불러와`", `"영화만들던거 불러와`", `"시네플로그`", 영화 파일 위치만 줘도 → 먼저 ``%USERPROFILE%\volcano_work\CLAUDE-시네플로그.md`` 를 읽고 그대로 따른다.`r`n"
  [System.IO.File]::AppendAllText($gc, $txt, (New-Object System.Text.UTF8Encoding $false))
  Write-Host "  Claude 지침(.claude\CLAUDE.md)에 시네플로그 단락을 넣었어요."
}

# 작업 폴더 + 제미나이 녹음 도구
if (Test-Path "D:\") { $w = "D:\cine_work" } else { $w = "$H\cine_work" }
New-Item -ItemType Directory -Force "$w\tts" | Out-Null
Copy-Item "$here\시네플로그\gemini_tts\*" "$w\tts" -Force
Write-Host "  작업 폴더: $w"

# 캡컷 틀
if (Test-Path "D:\") {
  $c = "D:\다운로드\CapCut Drafts"; New-Item -ItemType Directory -Force $c | Out-Null
  foreach ($t in @("0826 (2)", "0826 (8)")) { if (-not (Test-Path "$c\$t")) { Copy-Item "$here\캡컷틀\$t" "$c\$t" -Recurse } else { Write-Host "  캡컷 틀 $t 은 이미 있어서 그대로 둠" } }
} else { Write-Host "  [주의] D 드라이브가 없어요. 캡컷틀 폴더의 두 틀을 캡컷 프로젝트 위치에 직접 넣고, 스크립트의 'D:/다운로드/CapCut Drafts' 를 그 위치로 바꿔야 해요(Claude 에게 말하면 고쳐 줘요)." }

# 글꼴 (내 계정용)
$fd = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"; New-Item -ItemType Directory -Force $fd | Out-Null
$reg = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
foreach ($f in Get-ChildItem "$here\fonts") {
  $dst = "$fd\$($f.Name)"
  if (-not (Test-Path $dst)) { Copy-Item $f.FullName $dst }
  New-ItemProperty -Path $reg -Name "$($f.BaseName) (TrueType)" -Value $dst -PropertyType String -Force | Out-Null
}

New-Item -ItemType Directory -Force "$H\.volcano\keys" | Out-Null
python "$p\check_setup.py"
Start-Process "$H\.volcano\keys"
