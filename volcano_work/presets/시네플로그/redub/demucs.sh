#!/bin/bash
# 나레 뺀 배경(no_vocals) — 통째로 돌리면 메모리 부족으로 다른 작업까지 꺼짐(10-31) → 10분씩 끊어 돌리고 잇는다.
# 사용: bash demucs.sh /d/cine_work/redub_xxx
W=$1; cd "$W" || exit 1; mkdir -p dm
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 src.mp4 | cut -d. -f1)
for ((s=0; s<=D; s+=600)); do
  n=$(printf "%05d" $s); [ -f dm/$n/no_vocals.wav ] && continue
  ffmpeg -v error -y -ss $s -t 600 -i src.mp4 -vn -ac 2 -ar 44100 dm/c$n.wav
  python -m demucs --two-stems vocals -n htdemucs -j 2 -o dm/sep dm/c$n.wav >> demucs.log 2>&1
  mkdir -p dm/$n && mv dm/sep/htdemucs/c$n/no_vocals.wav dm/$n/ && rm -rf dm/sep/htdemucs/c$n dm/c$n.wav
  echo chunk $s / $D done
done
(cd dm && ls */no_vocals.wav | sort | sed "s|^|file |") > dm/list.txt
mkdir -p sep/htdemucs/a && ffmpeg -v error -y -f concat -safe 0 -i dm/list.txt -c copy sep/htdemucs/a/no_vocals.wav && echo DEMUCS_ALL_DONE
