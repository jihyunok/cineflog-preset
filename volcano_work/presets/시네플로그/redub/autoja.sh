# 사용: bash autoja.sh 이름 [nodlg] — 일본어판 tr → dlg → tts → subs → vf → (demucs 끝나면) mix
d=$1; W=D:/cine_work/redub_$d; R=~/volcano_work/presets/시네플로그/redub; cd $R
PYTHONIOENCODING=utf-8 python redub_ja.py setup $W
PYTHONIOENCODING=utf-8 python -u redub_ja.py tr $W > ${W}_ja/tr.log 2>&1; tail -n1 ${W}_ja/tr.log
[ "$2" = nodlg ] || { PYTHONIOENCODING=utf-8 python -u redub_ja.py dlg $W > ${W}_ja/dlg.log 2>&1; tail -n1 ${W}_ja/dlg.log; }
PYTHONIOENCODING=utf-8 python -u redub_ja.py tts $W > ${W}_ja/tts.log 2>&1; tail -n1 ${W}_ja/tts.log
PYTHONIOENCODING=utf-8 python redub_ja.py subs $W && PYTHONIOENCODING=utf-8 python redub_ja.py vf $W
until grep -q DEMUCS_ALL_DONE $W/demucs_run.log 2>/dev/null; do sleep 60; done
PYTHONIOENCODING=utf-8 python -u redub_ja.py mix $W > ${W}_ja/mix.log 2>&1; tail -n1 ${W}_ja/mix.log
