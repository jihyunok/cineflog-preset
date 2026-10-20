#!/bin/sh
# 21 쇼생크 탈출 준비 전체: 받아쓰기(원본 avi 소리로 바로) · 벤치 받아쓰기·지문 → prep1(1920 원본 뒤) → prep2
cd /c/cine_work/ep21_쇼생크탈출
P=C:/Users/최진영/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
python $P/sm.py "C:/Users/최진영/Downloads/쇼생크탈출 1995/The.avi" src_sm.json en --diar > sm_src.log 2>&1 &
python $P/sm.py bench/bench.mp4 bench/asr_sm.json ko > sm_bench.log 2>&1 &
python $P/fp.py bench/bench.mp4 22 fp_bench.npy > fp_bench.log 2>&1
sh prep1.sh
wait
sh prep2.sh
