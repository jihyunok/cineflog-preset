import sys,json,subprocess,random
from PIL import Image
d=sys.argv[1]; cr=sys.argv[2] if len(sys.argv)>2 else open(f"redub_{d}/zoom_args.txt").read().split()[0]
w,h,x,y=map(int,cr.split(":"))
import os; D=json.load(open(f"redub_{d}_ja/dlg_ja.json",encoding="utf-8")) if os.path.exists(f"redub_{d}_ja/dlg_ja.json") else [[t,t+1,""] for t in range(100,7400,250)]
random.seed(1); P=random.sample(D,min(24,len(D)))
S=Image.new("RGB",(w,24*70))
for k,(a,b,_) in enumerate(P):
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str((a+b)/2),"-i",f"redub_{d}/src720.mp4","-frames:v","1","_s.png"])
    im=Image.open("_s.png").crop((x,y+h-70,x+w,y+h)); S.paste(im,(0,k*70))
S.save(f"strip_{d}.jpg",quality=80); print(d,cr)
