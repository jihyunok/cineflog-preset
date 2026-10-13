#!/bin/bash
# 새 gem wav 가 생기거나 8분이 지나면 끝난다(메인이 깨어나 크롬을 찔러 본다)
n0=$(ls /d/cine_work/ep*/gem/b*.wav 2>/dev/null | wc -l)
for i in $(seq 1 18); do
  sleep 10
  n=$(ls /d/cine_work/ep*/gem/b*.wav 2>/dev/null | wc -l)
  [ "$n" -gt "$n0" ] && { echo "NEW $n"; exit 0; }
done
echo "TICK $n0"
