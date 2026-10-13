# -*- coding: utf-8 -*-
"""원본에 박힌 한국어 자막이 실제로 떠 있는 순간을 프레임으로 잰다(10-12 "5분4초부분에 고 글자가 늦게나와" — subev 시각이 화면과 어긋남).
벤치 편집표 컷마다 원본 구간을 8fps 로 자막 자리(y 560~780, x 360~1560)만 잘라, 흰 글자+검은 테두리 픽셀 수로 판정.
결과 burn.json {컷번호: [[시작, 끝](컷 안 초), ...]} — build_v6 가 확대 구간·대사 자막 시각을 여기에 맞춘다."""
import json, subprocess, numpy as np
from concurrent.futures import ThreadPoolExecutor
FPS = 8; Y0, HH, X0, WW = 560, 220, 360, 1200
E = json.load(open("edl.json")); F = 24000 / 1001
def frames(s0, L):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(s0, 0):.3f}", "-t", f"{L:.3f}", "-i", "../ep16v4_핀치/src.mp4",
                        "-vf", f"fps={FPS},crop={WW}:{HH}:{X0}:{Y0},scale={WW//2}:{HH//2},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.uint8).reshape(-1, HH // 2, WW // 2)
def score(a):
    w = a > 225; d = a < 50
    nb = np.zeros_like(w)
    for dy, dx in ((1, 0), (2, 0), (0, 1), (0, 2), (-1, 0), (0, -1)):
        nb |= np.roll(np.roll(d, dy, 0), dx, 1)
    return int((w & nb).sum())
def top(a):
    w = a > 225; r = np.where(w.sum(1) > 4)[0]
    return int(Y0 + r.min() * 2) if len(r) else 700
def one(k):
    g = E[k]; a = frames(g["s0"], g["d"]); sc = [score(x) for x in a]
    spans = []; i = 0
    while i < len(sc):          # 글자 있음 + 점수가 크게 바뀌면 다른 줄(자막이 바뀜)
        if sc[i] > 60:
            j = i + 1
            while j < len(sc) and sc[j] > 60 and abs(sc[j] - sc[i]) <= max(25, 0.12 * sc[i]): j += 1
            if j - i >= 2: spans.append([round(i / FPS, 3), round(j / FPS, 3), min(top(a[x]) for x in range(i, j))])
            i = j
        else: i += 1
    return k, spans
with ThreadPoolExecutor(6) as ex: R = dict(ex.map(one, range(len(E))))
json.dump(R, open("burn.json", "w"))
print("컷", len(R), "· 박힌 자막 있는 컷", sum(1 for v in R.values() if v), "· 총", round(sum(b - a for v in R.values() for a, b, _ in v)), "초")
