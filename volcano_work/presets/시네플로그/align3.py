import json,os,re,subprocess,time,uuid,urllib.request,urllib.error,difflib
from ko3 import KO
exec(open("align_d2.py",encoding="utf-8").read().split("res=json.load")[0].split("from d2_list import L")[1])
P=json.load(open("plan2.json",encoding="utf-8"))
res=json.load(open("d3_align.json",encoding="utf-8")) if os.path.exists("d3_align.json") else {}
for i,p in enumerate(P):
    if not p.get("new") or i not in KO or str(i) in res: continue
    s=p["s"]; ph=p["en"]; w0=max(0,s-6); f=f"dal/g{i:03d}.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(w0),"-t","14","-i","src.mp4","-vn","-ac","1","-ar","16000",f],check=True)
    words=asr(f).get("words",[])
    tgt=[norm(x) for x in ph.split() if norm(x)]; ws=[norm(w["word"]) for w in words]
    best=(0,None)
    for k in range(len(ws)):
        for n in range(max(1,len(tgt)-2),min(len(tgt)+3,len(ws)-k+1)):
            sc=difflib.SequenceMatcher(None,tgt,ws[k:k+n]).ratio()
            if sc>best[0]: best=(sc,(k,n))
    r={"score":0}
    if best[1]:
        k,n=best[1]; r={"score":round(best[0],2),"st":round(w0+words[k]["start"],2),"en":round(w0+words[k+n-1]["end"],2)}
    res[str(i)]=r; print(i,ph,r,flush=True)
    json.dump(res,open("d3_align.json","w",encoding="utf-8"),indent=0); time.sleep(3.2)
