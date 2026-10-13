import json, subprocess, os
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor
EV=[e for e in json.load(open("subev.json")) if e["s"]<6443]
os.makedirs("ocr",exist_ok=True)
def grab(e):
    p=f"ocr/{e['id']}.png"
    if not os.path.exists(p):
        t=(e["s"]+e["e"])/2
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{t:.2f}","-i","src.mp4","-frames:v","1","-vf","crop=1440:136:240:562,scale=900:85",p])
with ThreadPoolExecutor(6) as ex: list(ex.map(grab,EV))
N=30
for k in range(0,len(EV),N):
    rows=[]
    for e in EV[k:k+N]:
        im=Image.open(f"ocr/{e['id']}.png").convert("RGB"); c=Image.new("RGB",(1000,85),"black"); c.paste(im,(100,0))
        ImageDraw.Draw(c).text((4,35),str(e['id']),fill="yellow"); rows.append(c)
    S=Image.new("RGB",(1000,85*len(rows)))
    for r,im in enumerate(rows): S.paste(im,(0,r*85))
    S.save(f"ocrall_{k//N:02d}.png")
print(len(EV),(len(EV)+N-1)//N)
