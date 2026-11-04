#!/bin/sh
cd /d/cine_work/ep24_아포칼립스Z
P=C:/Users/uere/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
python $P/sm.py src.mp4 src_sm.json es --diar > sm_src.log 2>&1 &
python $P/sm.py bench/bench.mp4 bench/asr_sm.json ko > sm_bench.log 2>&1 &
python $P/scenes.py > scenes.log 2>&1
python $P/fp.py src.mp4 0 fp_src.npy > fp_src.log 2>&1
python $P/fp.py bench/bench.mp4 100 fp_bench.npy > fp_bench.log 2>&1
python $P/../black_map.py src.mp4 > black.log 2>&1
wait
python $P/lines_sm.py > lines_sm.log 2>&1
python $P/match.py > match.log 2>&1
python $P/edl.py > edl.log 2>&1
python $P/shot_desc.py --workers 5 > shot_desc.log 2>&1 &
python ko_ocr_1080.py --workers 3 > ko_ocr.log 2>&1 &
python $P/dcand.py > dcand.log 2>&1
python $P/jev_bench.py > jev_bench.log 2>&1
python $P/bench_flow.py > bench_flow.log 2>&1
wait
echo ALLDONE > prep.done
