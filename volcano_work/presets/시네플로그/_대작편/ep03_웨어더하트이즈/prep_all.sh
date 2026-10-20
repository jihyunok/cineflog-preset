#!/bin/sh
# 22 웨어 더 하트 이즈 준비 전체: 받아쓰기(원본·벤치) · 지문 → prep1 → prep2
cd /c/Users/Administrator/cine_work/ep03_웨어더하트이즈
P=C:/Users/Administrator/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
python $P/sm.py src.mp4 src_sm.json en --diar > sm_src.log 2>&1 &
python $P/sm.py bench/bench.mp4 bench/asr_sm.json ko > sm_bench.log 2>&1 &
python $P/fp.py bench/bench.mp4 0 fp_bench.npy > fp_bench.log 2>&1
sh prep1.sh
wait
sh prep2.sh
