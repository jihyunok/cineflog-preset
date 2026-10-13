import subprocess, sys
a, b, n, out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
st = (b - a) / n; fs = []
for k in range(n):
    t = a + k * st; f = f"fr/s_{k}.jpg"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{t:.2f}","-i","src.mp4","-frames:v","1","-vf",f"scale=384:-1",f])
    fs.append(f)
cols = 5; rows = (n + cols - 1) // cols
inp = sum([["-i", f] for f in fs], [])
lay = "|".join(f"{(k%cols)*384}_{(k//cols)*216}" for k in range(n))
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",f"xstack=inputs={n}:layout={lay}:fill=black",out])
