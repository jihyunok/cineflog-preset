#!/bin/bash
# 이 편만: gem/bKK_n0_n1.wav 가 생기면 gem_split 으로 narr/nNNN.wav·json 으로 자른다(04 splitwatch04.sh 꼴). 결과는 gem/bKK.split.log
# 묶음 수는 batches.json 에서 읽어, 마지막 묶음까지 다 자르면 끝난다.
cd /d/cine_work/ep06v2_로드하우스
NB=$(python -c "import json;print(len(json.load(open('batches.json',encoding='utf-8'))))")
while true; do
  for w in gem/b*.wav; do
    [ -f "$w" ] || continue
    [ -f "$w.split.log" ] && continue
    sleep 3
    b=$(basename "$w" .wav); n0=$(echo $b | cut -d_ -f2); n1=$(echo $b | cut -d_ -f3)
    PYTHONIOENCODING=utf-8 python /c/Users/uere/volcano_work/presets/시네플로그/gemini_tts/gem_split.py "$w" $((10#$n0)) $((10#$n1)) --out narr > "$w.split.log" 2>&1
    echo "rc=$?" >> "$w.split.log"
  done
  [ $(ls gem/*.split.log 2>/dev/null | wc -l) -ge $NB ] && break
  sleep 15
done
echo SPLITDONE
