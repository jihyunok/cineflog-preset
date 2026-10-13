import subprocess, numpy as np
W,H,FPS=480,74,2
p=subprocess.Popen(["ffmpeg","-v","error","-i","src.mp4","-vf",f"fps={FPS},crop=960:148:960:500,scale={W}:{H},format=gray","-f","rawvideo","-"],stdout=subprocess.PIPE)
k=0; out=[]
while True:
    b=p.stdout.read(W*H)
    if len(b)<W*H: break
    a=np.frombuffer(b,np.uint8).reshape(H,W).astype(np.int16)
    br=a>200; dk=np.zeros_like(br); dk[:,2:]|=a[:,:-2]<90; dk[:,:-2]|=a[:,2:]<90
    out.append(int((br&dk).sum())); k+=1
np.save("tmp/loc.npy",np.array(out)); print(k)
