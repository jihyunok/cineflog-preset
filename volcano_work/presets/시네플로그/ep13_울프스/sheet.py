import subprocess, sys
from PIL import Image, ImageDraw
a, b, step, out = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
ts = []; t = a
while t <= b: ts.append(t); t += step
ims = []
for t in ts:
    p = subprocess.run(["ffmpeg","-v","error","-ss",f"{t:.2f}","-i","src.mp4","-frames:v","1","-vf","scale=384:160","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    im = Image.frombytes("RGB",(384,160),p); ImageDraw.Draw(im).text((4,4),f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:04.1f}",fill="yellow"); ims.append(im)
C = 5; R = (len(ims)+C-1)//C
S = Image.new("RGB",(384*C,160*R))
for i, im in enumerate(ims): S.paste(im,((i%C)*384,(i//C)*160))
S.save(out, quality=80)
