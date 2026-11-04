#!/bin/bash
# 무비세상 B판: 남은 편 init → rewrite → emph 를 차례로(녹음 전까지). 10-31
cd ~/volcano_work/presets/시네플로그/b판
export PYTHONIOENCODING=utf-8   # 10-31 agy 클로드 할당량 105시간 막힘 → 제미나이(기본)
for A in ep20_패밀리플랜2 ep14v2_더픽업 ep06v2_로드하우스 ep05v2_토탈리킬러 ep04v2_위드아웃리모스 ep03v2_아이돈언더스탠드유; do
  n=$(echo $A | sed -E 's/^ep([0-9]+)(v[0-9]+)?_(.*)$/ep\1b_\3/'); B=D:/cine_work/$n
  echo "== $A → $n $(date +%H:%M)"
  [ -f "$B/narr_b.json" ] || python make_b.py init D:/cine_work/$A || { echo "INIT FAIL $A"; continue; }
  python make_b.py rewrite "$B" || { echo "REWRITE FAIL $A"; continue; }
  python make_b.py emph "$B" || echo "EMPH FAIL $A"
done
echo ALLDONE
