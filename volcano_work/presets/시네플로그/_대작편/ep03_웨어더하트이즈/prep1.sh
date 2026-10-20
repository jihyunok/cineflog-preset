#!/bin/sh
# 22 준비 1단계: 컷 · 그림 지문 · 까만 화면 (원본 받아쓰기 끝까지 기다림)
cd /c/Users/Administrator/cine_work/ep03_웨어더하트이즈
P=C:/Users/Administrator/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
python $P/scenes.py > scenes.log 2>&1 &
python $P/fp.py src.mp4 0 fp_src.npy > fp_src.log 2>&1 &
python $P/../black_map.py src.mp4 > black.log 2>&1
wait
until [ -f src_sm.json ]; do sleep 20; done
echo ALLDONE > prep1.done
