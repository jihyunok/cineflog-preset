# 완성본에서 박힌 자막이 남았는지: 2fps 로 그림 안(y700~860, 우리 자막 위) 흰 글자+검은 가장자리 픽셀을 세어 의심 시각을 뽑는다
import subprocess, numpy as np, sys
W, H, FPS = 960, 80, 2
p = subprocess.Popen(["ffmpeg","-v","error","-i",sys.argv[1] if len(sys.argv)>1 else "final.mp4","-vf",f"fps={FPS},crop=1920:160:0:700,scale={W}:{H},format=gray","-f","rawvideo","-"], stdout=subprocess.PIPE)
hits = []; k = 0
while True:
    b = p.stdout.read(W*H)
    if len(b) < W*H: break
    a = np.frombuffer(b, np.uint8).reshape(H, W).astype(np.int16)
    br = a > 215; dk = np.zeros_like(br); dk[:, 2:] |= a[:, :-2] < 100; dk[:, :-2] |= a[:, 2:] < 100
    if (br & dk).sum() > 60: hits.append(k / FPS)
    k += 1
print("의심", len(hits), [round(x, 1) for x in hits[:80]])
