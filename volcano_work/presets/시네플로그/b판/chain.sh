#!/bin/bash
# 무비세상 B판: 대본까지 된 편을 차례로 finish_b (새 ⑨ 걸리면 멈춤 · 일레븐랩스 글자 모자라면 멈춤). 10-31
cd ~/volcano_work/presets/시네플로그/b판; export PYTHONIOENCODING=utf-8 AGY_MODEL=claude-sonnet-5-5-medium
for n in ep20b_패밀리플랜2 ep23b_배신의만찬; do   # 10-31 사용자 「일래븐으로하면되지」 → 제미나이 한도 기다리지 않고 일레븐으로 처음부터
  B=D:/cine_work/$n
  [ -f "$B/final.mp4" ] && continue
  until grep -q "^== " /d/cine_work/b_prep_all3.log && { grep -q "ALLDONE" /d/cine_work/b_prep_all3.log || [ -n "$(grep -A99 "→ $n" /d/cine_work/b_prep_all3.log | grep -m1 '^emph\|EMPH FAIL')" ]; }; do sleep 60; done
  need=$(python -c "import json;ns={};exec(open('$B/script.py',encoding='utf-8').read(),ns);print(sum(len(x[1]) for x in ns['S'] if x[0]=='N'))")
  left=$(python -c "import json,urllib.request,os;K=open(os.path.expanduser('~/.volcano/keys/elevenlabs')).read().strip();u=json.load(urllib.request.urlopen(urllib.request.Request('https://api.elevenlabs.io/v1/user/subscription',headers={'xi-api-key':K})));print(u['character_limit']-u['character_count'])")
  if [ "$left" -lt "$need" ]; then echo "QUOTA $n need $need left $left"; exit 4; fi
  echo "== $n $(date +%H:%M) need $need left $left"
  python finish_b.py "$B" $([ -f "$B/b_new9.txt" ] && echo --from plan) > "$B/_finish.log" 2>&1; rc=$?
  tail -3 "$B/_finish.log"
  if [ $rc -ne 0 ]; then echo "STOP $n rc $rc"; exit $rc; fi
done
echo CHAINDONE
