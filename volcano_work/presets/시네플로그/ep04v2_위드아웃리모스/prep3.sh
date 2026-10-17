#!/bin/sh
# 04v2 준비 3단계(10-16) — 어두운 영화라 컷 문턱 0.28 이 컷을 절반쯤 놓침 → 0.12 로 다시 잰 뒤 컷에 기대는 단계만 다시
cd /d/cine_work/ep04v2_위드아웃리모스
P=C:/Users/uere/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
python $P/scenes.py 0.12 > scenes.log 2>&1
python $P/shot_desc.py --workers 6 > shot_desc.log 2>&1 &
python $P/edl.py > edl.log 2>&1
python $P/bench_flow.py > bench_flow.log 2>&1
python $P/dcand.py > dcand.log 2>&1
wait
echo ALLDONE > prep3.done
