#!/bin/sh
cd /d/cine_work/ep23_배신의만찬
P=C:/Users/uere/volcano_work/presets/시네플로그/v9/prep
export PYTHONIOENCODING=utf-8
ffmpeg -v error -y -i orig.mkv -map 0:0 -map 0:1 -c:v h264_nvenc -preset p5 -rc vbr -cq 17 -pix_fmt yuv420p -c:a aac -ac 2 -ar 48000 -b:a 192k -movflags +faststart src.mp4 > conv.log 2>&1
python -c "import json,subprocess;e=json.load(open('ep.json',encoding='utf-8'));e['srclen']=round(float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','src.mp4'],capture_output=True,text=True).stdout),3);json.dump(e,open('ep.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)"
python $P/sm.py src.mp4 src_sm.json en --diar > sm_src.log 2>&1 &
python $P/sm.py bench/bench.mp4 bench/asr_sm.json ko > sm_bench.log 2>&1 &
python $P/scenes.py > scenes.log 2>&1
python $P/fp.py src.mp4 0 fp_src.npy > fp_src.log 2>&1
python $P/fp.py bench/bench.mp4 150 fp_bench.npy > fp_bench.log 2>&1
python $P/../black_map.py src.mp4 > black.log 2>&1
wait
python $P/lines_sm.py > lines_sm.log 2>&1
python $P/match.py > match.log 2>&1
python $P/edl.py > edl.log 2>&1
python $P/shot_desc.py --workers 6 > shot_desc.log 2>&1 &
python $P/dcand.py > dcand.log 2>&1
python ko_ref.py > ko_ref.log 2>&1
python $P/jev_bench.py > jev_bench.log 2>&1
python $P/bench_flow.py > bench_flow.log 2>&1
wait
echo ALLDONE > prep.done
