#!/bin/sh
# 21 준비 1단계 — 원본 1920x1024(pad.log ok) 뒤: 컷 · 그림 지문 · 까만 화면
cd /c/cine_work/ep21_쇼생크탈출
P=C:/Users/최진영/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
until grep -q ok pad.log 2>/dev/null; do sleep 20; done
python $P/scenes.py > scenes.log 2>&1 &
python $P/fp.py src.mp4 0 fp_src.npy > fp_src.log 2>&1 &
python $P/../black_map.py src.mp4 > black.log 2>&1
wait
until [ -f src_sm.json ]; do sleep 20; done
echo ALLDONE > prep1.done
