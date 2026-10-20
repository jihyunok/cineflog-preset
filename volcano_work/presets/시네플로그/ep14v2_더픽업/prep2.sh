#!/bin/sh
# 03v2 준비 2단계 — prep1 끝난 뒤: 대사 줄표 · 벤치 대조 · 벤치 흐름 · 컷 그림 설명(agy)
cd /d/cine_work/ep14v2_더픽업
P=C:/Users/uere/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
until [ -f prep1.done ]; do sleep 20; done
python $P/shot_desc.py --workers 6 > shot_desc.log 2>&1 &
python $P/lines_sm.py > lines_sm.log 2>&1
python $P/match.py > match.log 2>&1
python $P/edl.py > edl.log 2>&1
python $P/jev_bench.py > jev_bench.log 2>&1
python $P/bench_flow.py > bench_flow.log 2>&1
python $P/dcand.py > dcand.log 2>&1
wait
echo ALLDONE > prep2.done
