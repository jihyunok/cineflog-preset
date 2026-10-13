# -*- coding: utf-8 -*-
"""나레 조각 wav 마다 귀에 걸리는 증상 검사 (10-13 「고」·「그 곳까지」): 맨 앞 짧은 소리 토막(<0.35초) 뒤 0.2초+ 쉼 /
맨 끝 0.2초+ 쉼 뒤 짧은 토막 / 끝이 소리 속에서 뚝 끊김(마지막 20ms > -30dB). 사용: python narr_frag.py [SKIP 번호...]"""
import glob, sys, subprocess, numpy as np
SR = 16000; HOP = 0.01
SKIP = {int(x) for x in sys.argv[1:]} or {119}
def load(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.float32)
bad = 0
for p in sorted(glob.glob("narr/n[0-9][0-9][0-9].wav")):
    i = int(p[6:9])
    if i in SKIP: continue
    x = load(p); n = int(HOP * SR); m = len(x) // n
    db = 20 * np.log10(np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(1) + 1e-12))
    s = db < -40; runs = []; k = 0
    while k < m:
        j = k
        while j < m and s[j] == s[k]: j += 1
        runs.append((bool(s[k]), k * HOP, j * HOP)); k = j
    snd = [r for r in runs if not r[0]]; sil = [r for r in runs if r[0] and r[2] - r[1] >= 0.2]
    why = []
    if snd and sil and snd[0][2] - snd[0][1] < 0.35 and sil[0][1] <= snd[0][2] + 0.01: why.append(f"앞 토막 {snd[0][2] - snd[0][1]:.2f}초+쉼 {sil[0][2] - sil[0][1]:.2f}")
    if snd and sil and snd[-1][2] - snd[-1][1] < 0.35 and abs(sil[-1][2] - snd[-1][1]) < 0.011: why.append(f"끝 토막 {snd[-1][2] - snd[-1][1]:.2f}초(쉼 {sil[-1][2] - sil[-1][1]:.2f} 뒤)")
    if db[-2:].max() > -30: why.append(f"끝 뚝 {db[-2:].max():.0f}dB")
    if why: bad += 1; print(f"n{i:03d} {m * HOP:.2f}초", " · ".join(why))
print("증상 있는 조각", bad)
