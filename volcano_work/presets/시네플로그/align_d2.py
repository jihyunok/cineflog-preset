import json,os,re,subprocess,time,uuid,urllib.request,urllib.error,difflib
from d2_list import L
KEY=open(os.path.expanduser("~/.volcano/keys/groq"),encoding="utf-8").read().strip()
norm=lambda w: re.sub(r"[^a-z0-9']","",w.lower())
def asr(p):
    b="----x"+uuid.uuid4().hex; parts=[]
    for k,v in [("model","whisper-large-v3"),("response_format","verbose_json"),("temperature","0"),("language","en"),("timestamp_granularities[]","word")]:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode()); parts.append(open(p,"rb").read()); parts.append(f"\r\n--{b}--\r\n".encode())
    while True:
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions",data=b"".join(parts),headers={"Authorization":"Bearer "+KEY,"Content-Type":"multipart/form-data; boundary="+b,"User-Agent":"curl/8"}),timeout=120))
        except urllib.error.HTTPError as e:
            print("  ",e.code,e.read().decode()[:150],flush=True)
            if e.code==429: time.sleep(30); continue
            raise
res=json.load(open("d2_align.json",encoding="utf-8")) if os.path.exists("d2_align.json") else {}
for i,(blk,split,ph,s,ko) in enumerate(L):
    key=f"{blk}|{ph}"
    if key in res: continue
    w0=max(0,s-8); p=f"dal/e{i:02d}.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(w0),"-t","18","-i","src.mp4","-vn","-ac","1","-ar","16000",p],check=True)
    words=asr(p).get("words",[])
    tgt=[norm(x) for x in ph.split() if norm(x)]; ws=[norm(w["word"]) for w in words]
    best=(0,None)
    for k in range(len(ws)):
        for n in range(max(1,len(tgt)-2),min(len(tgt)+3,len(ws)-k+1)):
            sc=difflib.SequenceMatcher(None,tgt,ws[k:k+n]).ratio()
            if sc>best[0]: best=(sc,(k,n))
    r={"score":0}
    if best[1]:
        k,n=best[1]; r={"score":round(best[0],2),"st":round(w0+words[k]["start"],2),"en":round(w0+words[k+n-1]["end"],2),"got":" ".join(w["word"] for w in words[k:k+n])}
    res[key]=r; print(i,blk,ph,"->",r,flush=True)
    json.dump(res,open("d2_align.json","w",encoding="utf-8"),ensure_ascii=False,indent=0); time.sleep(3.2)
