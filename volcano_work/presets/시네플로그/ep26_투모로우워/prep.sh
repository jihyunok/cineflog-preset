#!/bin/sh
# 26 투모로우 워 준비 — 벤치 없음(24·25편처럼 영화 순서), 박힌 한국어 자막 → ko_ocr.py 로 srt.txt
cd /d/cine_work/ep26_투모로우워
P=C:/Users/uere/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
python -c "import json,subprocess;e=json.load(open('ep.json',encoding='utf-8'));e['srclen']=round(float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','src.mp4'],capture_output=True,text=True).stdout),3);json.dump(e,open('ep.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)"
python $P/sm.py src.mp4 src_sm.json en --diar > sm_src.log 2>&1 &
python $P/scenes.py > scenes.log 2>&1
python $P/../black_map.py src.mp4 > black.log 2>&1
wait
python $P/lines_sm.py > lines_sm.log 2>&1
python $P/shot_desc.py --workers 5 > shot_desc.log 2>&1 &
python ko_ocr.py --workers 3 > ko_ocr.log 2>&1 &
python $P/dcand.py > dcand.log 2>&1
wait
echo ALLDONE > prep.done
