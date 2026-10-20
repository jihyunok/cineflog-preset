#!/bin/sh
# 03v2 준비 전체: 벤치 받아쓰기·지문(지금) + prep1(원본 1920 뒤) → prep2
cd /d/cine_work/ep14v2_더픽업
P=C:/Users/uere/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
python $P/sm.py bench/bench.mp4 bench/asr_sm.json ko > sm_bench.log 2>&1 &
python $P/fp.py bench/bench.mp4 60 fp_bench.npy > fp_bench.log 2>&1
sh prep1.sh
wait
sh prep2.sh
