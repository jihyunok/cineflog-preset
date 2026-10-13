import subprocess, numpy as np, json
W, H, FPS = 600, 72, 5
p = subprocess.Popen(["ffmpeg","-v","error","-i","src.mp4","-vf",f"fps={FPS},crop=1200:144:360:650,scale={W}:{H},format=gray","-f","rawvideo","-"], stdout=subprocess.PIPE)
fr = []; k = 0
while True:
    b = p.stdout.read(W*H)
    if len(b) < W*H: break
    a = np.frombuffer(b, np.uint8).reshape(H, W).astype(np.int16)
    br = a > 215
    dk = np.zeros_like(br)
    dk[:, 2:] |= a[:, :-2] < 100; dk[:, :-2] |= a[:, 2:] < 100
    m = br & dk
    fr.append(np.packbits(m).tobytes()); k += 1
np.save("masks.npy", np.array([np.frombuffer(x, np.uint8) for x in fr]))
print("frames", k)
