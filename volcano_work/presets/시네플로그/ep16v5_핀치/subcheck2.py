# -*- coding: utf-8 -*-
"""의심 줄만 앞뒤 8초씩 짧게 받아써서 다시 잰다. 사용: python subcheck2.py 영상 자막.ass 시각,시각,..."""
import re, sys, subprocess, os
sys.argv_save = sys.argv[:]
exec(open("subcheck.py", encoding="utf-8").read().split("W = []")[0].replace("V, A = sys.argv[1], sys.argv[2]", "V, A = sys.argv_save[1], sys.argv_save[2]"))
def ts(x):
    h, m, s = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
L = [l.rstrip("\n").split(",", 9) for l in open(A, encoding="utf-8") if l.startswith("Dialogue") and ",N,," in l]
for q in [float(x) for x in sys.argv_save[3].split(",")]:
    f = min(L, key=lambda f: abs(ts(f[1]) - q)); a = ts(f[1]); t = f[9]
    m = "_c2.mp3"; s0 = max(0, a - 8)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s0), "-t", "16", "-i", V, "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k", m], check=True)
    W = [(s0 + w["start"], w["word"]) for w in asr(m).get("words", [])]
    first = re.sub(r"[^가-힣0-9A-Za-z]", "", t.split(" ")[0])[:2]
    c = [wt for wt, ww in W if re.sub(r"[^가-힣0-9A-Za-z]", "", ww).startswith(first)]
    d = round(min(c, key=lambda x: abs(x - a)) - a, 2) if c else None
    print(round(a, 1), d, t, "|", " ".join(f"{wt:.1f}:{ww}" for wt, ww in W if abs(wt - a) < 4)[:160])
    os.remove(m)
