# -*- coding: utf-8 -*-
"""그림 지문: 화면 가운데 띠(자막 피함)를 48x18 회색으로 줄여 4fps 로 저장. 사용: python fp.py 영상 위y 출력.npy"""
import subprocess, sys, numpy as np
src, y0, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
FPS, WW, HH = 4, 48, 18
vf = f"fps={FPS},crop=1920:480:0:{y0 + 80},scale={WW}:{HH}:flags=area,format=gray"
p = subprocess.run(["ffmpeg", "-v", "error", "-threads", "8", "-i", src, "-vf", vf, "-f", "rawvideo", "-"], capture_output=True)
a = np.frombuffer(p.stdout, np.uint8).reshape(-1, HH, WW).astype(np.float32)
np.save(out, a)
print(out, a.shape)
