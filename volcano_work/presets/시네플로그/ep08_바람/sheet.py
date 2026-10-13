import subprocess, sys, os
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor
a, b, step, tag = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
os.makedirs("v", exist_ok=True)
ts = [a + k * step for k in range(int((b - a) / step) + 1)]
def g(t):
    p = f"v/{t:.1f}.jpg"
    if not os.path.exists(p): subprocess.run(["ffmpeg","-v","error","-y","-ss",str(t),"-i","src.mp4","-frames:v","1","-vf","scale=320:180",p])
    return p
with ThreadPoolExecutor(6) as ex: ps = list(ex.map(g, ts))
S=Image.new("RGB",(320*6,180*((len(ps)+5)//6)))
for k,(t,p) in enumerate(zip(ts,ps)):
    im=Image.open(p).convert("RGB"); ImageDraw.Draw(im).text((4,3),f"{t:.1f}",fill="yellow"); S.paste(im,((k%6)*320,(k//6)*180))
S.save(f"v_{tag}.jpg",quality=78)
