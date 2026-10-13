# 원본 y470~634(크롭 안쪽)에 박힌 자막 같은 글자(흰 글자+검은 테두리)가 뜨는 시각 → hisub.json
import subprocess, numpy as np, json
W, H, FPS = 600, 82, 2
p = subprocess.Popen(["ffmpeg","-v","error","-i","src.mp4","-vf",f"fps={FPS},crop=1200:164:360:470,scale={W}:{H},format=gray","-f","rawvideo","-"], stdout=subprocess.PIPE)
hits = []; k = 0
while True:
    b = p.stdout.read(W*H)
    if len(b) < W*H: break
    a = np.frombuffer(b, np.uint8).reshape(H, W).astype(np.int16)
    br = a > 215; dk = np.zeros_like(br); dk[:, 2:] |= a[:, :-2] < 60; dk[:, :-2] |= a[:, 2:] < 60
    n = int((br & dk).sum())
    if n > 60: hits.append((round(k / FPS, 1), n))
    k += 1
json.dump(hits, open("hisub.json", "w"))
print(len(hits))
