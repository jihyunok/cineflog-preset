import subprocess, sys, os
from PIL import Image, ImageDraw
rows=[]
for c in [float(x) for x in sys.argv[1:]]:
    row=[]
    for k in range(8):
        t=c+k*1.0; p=f"v/f{t:.1f}.jpg"
        if not os.path.exists(p): subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{t:.2f}","-i","src.mp4","-frames:v","1","-vf","scale=400:-2",p])
        im=Image.open(p).convert("RGB"); ImageDraw.Draw(im).text((5,4),f"{t:.1f}",fill="yellow"); row.append(im)
    rows.append(row)
w,h=rows[0][0].size; S=Image.new("RGB",(w*8,h*len(rows)))
for r,row in enumerate(rows):
    for k,im in enumerate(row): S.paste(im,(k*w,r*h))
S.save("fine4.jpg",quality=82)
