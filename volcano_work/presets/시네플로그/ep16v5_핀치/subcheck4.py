# -*- coding: utf-8 -*-
"""나레 자막 ↔ 목소리 대조 4판 (10-13) — 받아쓰기 없이 나레만 든 트랙의 소리 크기로 잰다.
subcheck·subcheck3 은 Whisper 가 문장 앞 쉼을 첫 낱말에 붙여 '목소리가 자막보다 0.5~1.4초 먼저' 라는 가짜를 냈다
(7:18 「날씨 자료를」: 실제 목소리 시작 0.89초 = 자막 0.88초).
판정: ① 자막이 떴는데 목소리가 0.4초 넘게 안 나옴(자막 빠름) ② 앞 줄이 끝나고 목소리가 시작됐는데 자막이 0.4초 넘게 늦게 뜸(자막 늦음)
③ 목소리가 나오는데 자막이 0.6초 넘게 비어 있음.
사용: python subcheck4.py narr_track8.wav subs_v8.ass"""
import subprocess, sys, numpy as np
V, A = sys.argv[1], sys.argv[2]
b = subprocess.run(["ffmpeg", "-v", "error", "-i", V, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
x = np.frombuffer(b, np.float32); F = 160
e = np.sqrt(np.mean(x[:len(x) // F * F].reshape(-1, F) ** 2, 1))       # 10ms
on = e > 0.02
k = 0                                                                   # 0.15초 안 짧은 끊김은 말 안 (자음·숨)
while k < len(on):
    if not on[k]:
        j = k
        while j < len(on) and not on[j]: j += 1
        if j - k < 15 and k > 0: on[k:j] = True
        k = j
    else: k += 1
def ts(s):
    h, m, c = s.split(":"); return int(h) * 3600 + int(m) * 60 + float(c)
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
L = sorted((ts(l.split(",")[1]), ts(l.split(",")[2]), l.rstrip("\n").split(",", 9)[9]) for l in open(A, encoding="utf-8") if l.startswith("Dialogue") and ",N,," in l)
def fr(t): return min(max(int(t * 100), 0), len(on) - 1)
early, late, hole = [], [], []
for i, (a, z, t) in enumerate(L):
    if not on[fr(a)]:
        j = fr(a)
        while j < len(on) and not on[j]: j += 1
        if j / 100 - a > 0.4 and j / 100 < z: early.append((mm(a), round(j / 100 - a, 2), t))
    else:
        j = fr(a)
        while j > 0 and on[j - 1]: j -= 1                                # 지금 말 덩어리의 시작
        prev_end = L[i - 1][1] if i else 0
        if a - j / 100 > 0.4 and j / 100 >= prev_end - 0.05: late.append((mm(a), round(a - j / 100, 2), t))
# ③ 목소리 있는데 자막 없는 곳
cov = np.zeros(len(on), bool)
for a, z, _ in L: cov[fr(a):fr(z)] = True
k = 0
while k < len(on):
    if on[k] and not cov[k]:
        j = k
        while j < len(on) and on[j] and not cov[j]: j += 1
        if j - k > 60: hole.append((mm(k / 100), round((j - k) / 100, 2)))
        k = j
    else: k += 1
print(f"나레 자막 {len(L)} · ① 자막 빠름 {len(early)} · ② 자막 늦음 {len(late)} · ③ 목소리에 자막 빔 {len(hole)}")
for n, v in (("①", early), ("②", late), ("③", hole)):
    for r in v: print(" ", n, r)
