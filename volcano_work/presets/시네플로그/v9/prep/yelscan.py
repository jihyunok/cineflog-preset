# -*- coding: utf-8 -*-
# 10-24 대작 08: 원본에 박힌 노란 글자(지명 카드·TV 뉴스 번역 등)가 보이는 조각 찾기 — 조각마다 처음·가운데·끝 프레임.
# 1:05 「FBI LOS ANGELES FIELD OFFICE」 카드의 노란 한국어 자막이 그림 가운데(y≈680)에 있어 FILL 자르기로 못 빼고 우리 자막과 겹쳤다 → 굽기 전 이걸로 찾고 그 줄 구간을 옮긴다.
# 사용: python yelscan.py [windows.json]  (지금 띠 = y540~840 그림 가운데 아래. 자막 띠를 보려면 crop 을 1320:200:300:820)
import json, subprocess, sys
import numpy as np
W = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "windows.json", encoding="utf-8"))
SRC = json.load(open("ep.json", encoding="utf-8"))["src"]
hit = []
for j, w in enumerate(W):
    L = (w["b"] - w["a"]) * w.get("rate", 1.05 if w["kind"] != "N" else 1.0)
    for t in (w["s"] + 0.1, w["s"] + L / 2, w["s"] + max(0.1, L - 0.15)):
        b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", SRC, "-frames:v", "1", "-vf", "crop=1320:300:300:540,scale=660:150", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        a = np.frombuffer(b, np.uint8).reshape(150, 660, 3).astype(int)
        y = (a[..., 0] > 190) & (a[..., 1] > 190) & (a[..., 2] < 90)
        if y.sum() > 120: hit.append((j, w["k"], round(t, 1), int(y.sum()))); break
print(len(hit)); [print(*h) for h in hit]
