#!/bin/sh
# 03 아이 돈 언더스탠드 유 다시 준비 1단계 — 원본 1920 맞춤(pad.log ok) 뒤: 받아쓰기(Speechmatics) · 컷 · 그림 지문 · 까만 화면
cd /d/cine_work/ep03v2_아이돈언더스탠드유
P=C:/Users/uere/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
until grep -q ok pad.log 2>/dev/null; do sleep 20; done
python $P/sm.py src.mp4 src_sm.json en --diar > sm_src.log 2>&1 &
python $P/scenes.py > scenes.log 2>&1
python $P/fp.py src.mp4 0 fp_src.npy > fp_src.log 2>&1
python $P/../black_map.py src.mp4 > black.log 2>&1
wait
echo ALLDONE > prep1.done
