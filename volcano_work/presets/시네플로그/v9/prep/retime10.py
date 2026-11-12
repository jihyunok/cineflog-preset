# -*- coding: utf-8 -*-
# 관문 ⑩ 자막↔목소리 어긋난 줄: wav 목소리 구간(쉼 0.15초+로 나눔)에 쉼표·마침표 덩어리를 맞춰 글자 시각을 다시 깐다(A판 _fix10 꼴). 사용: python _retime.py 글앞부분 ...
import json, os, re, shutil, subprocess, sys
import numpy as np
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
N = [x[1] for x in ns["S"] if x[0] == "N"]
os.makedirs("_fix10", exist_ok=True)
for key in sys.argv[1:]:
    n = next(i for i, t in enumerate(N, 1) if key in t); p = f"narr/n{n:03d}"
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", p + ".wav", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(b, np.float32); r = np.sqrt(np.mean(x[:len(x) // 160 * 160].reshape(-1, 160) ** 2, 1)); on = r > r.max() * 0.06
    segs = []; k = 0
    while k < len(on):
        if on[k]:
            j = k
            while j < len(on) and on[j]: j += 1
            if segs and k / 100 - segs[-1][1] < float(os.environ.get("GAP", "0.15")): segs[-1] = (segs[-1][0], j / 100)
            else: segs.append((k / 100, j / 100))
            k = j
        else: k += 1
    segs = [s for s in segs if s[1] - s[0] > 0.08]
    j = json.load(open(p + ".json", encoding="utf-8")); ch = j["chars"]
    cuts = [i + 1 for i, c in enumerate(ch) if c in ",." and i < len(ch) - 1]
    print(n, j["text"], "구간", [(round(a, 2), round(z, 2)) for a, z in segs], "쉼표", len(cuts))
    if len(segs) != len(cuts) + 1: print("  ✗ 구간 수와 덩어리 수가 달라 건너뜀"); continue
    if not os.path.exists(f"_fix10/n{n:03d}_orig.json"): shutil.copy(p + ".json", f"_fix10/n{n:03d}_orig.json")
    st = [0] * len(ch); en = [0] * len(ch)
    for (a, z), (i0, i1) in zip(segs, zip([0] + cuts, cuts + [len(ch)])):
        idx = [i for i in range(i0, i1) if ch[i].strip() and ch[i] not in ",.?!"]; d = (z - a) / max(1, len(idx)); pos = a
        for i in range(i0, i1):
            if i in idx: st[i] = round(pos, 3); pos += d; en[i] = round(pos, 3)
            else: st[i] = en[i] = round(pos, 3)
    j["st"], j["en"] = st, en; j["fix10"] = "10-23 관문 ⑩: 목소리 구간에 맞춰 글자 시각 다시 깔기"
    json.dump(j, open(p + ".json", "w", encoding="utf-8"), ensure_ascii=False); print("  고침")
