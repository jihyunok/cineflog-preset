#!/bin/sh
# 32 잭 리처: 네버 고 백 준비 — 벤치 없음(영화 순서), 박힌 한국어 자막 → ko_ocr.py 로 srt.txt (26편과 같은 길)
cd /d/cine_work/ep32_잭리처2
P=C:/Users/uere/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
F="C:/Users/uere/OneDrive/Desktop/밤파일 다운로드/[ 잭리처 시리즈 ]/(액션)[ 잭리처 시리즈 ]_2.mkv"
ffmpeg -v error -y -i "$F" -map 0:0 -map 0:1 -vf "crop=1920:804:0:138" -c:v h264_nvenc -preset p5 -rc vbr -cq 17 -pix_fmt yuv420p -c:a aac -ac 2 -ar 48000 -b:a 192k -movflags +faststart src.mp4 > conv.log 2>&1
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
python _tl.py > tl.log 2>&1
python _tlc.py > tlc.log 2>&1
echo ALLDONE > prep.done
