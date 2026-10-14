# -*- coding: utf-8 -*-
"""원본 0.25초마다 '진짜 까만 화면'인지 — 색 채널 중 가장 밝은 값의 98% 지점(RGB, 64x27).
10-13 17 그레이하운드: 회색 지문(fp_src)의 밝기 90% < 0.07 잣대는 붉은 조명 함교(전투 배치 밤 장면)를 까맣다고 봤다 → 색까지 본다.
사용: python black_map.py 원본 [출력=black_src.npy]  → float32 배열(0~1, 작을수록 까맘). 까만 화면 = 값 < 0.08"""
import subprocess, sys, numpy as np
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else "black_src.npy"
W, H = 64, 27
p = subprocess.Popen(["ffmpeg", "-v", "error", "-threads", "8", "-i", src, "-vf", f"fps=4,scale={W}:{H}:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
vals = []
while True:
    b = p.stdout.read(W * H * 3 * 512)
    if not b: break
    a = np.frombuffer(b[:len(b) // (W * H * 3) * W * H * 3], np.uint8).reshape(-1, H * W, 3).max(2)
    vals.append(np.percentile(a, 98, axis=1) / 255)
v = np.concatenate(vals).astype(np.float32); np.save(out, v)
print(out, len(v), "· 까만(<0.08) 초", round(float((v < 0.08).sum() / 4), 1))
