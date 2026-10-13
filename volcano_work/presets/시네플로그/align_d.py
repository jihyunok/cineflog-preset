import json,os,re,subprocess,time,uuid,urllib.request,urllib.error,difflib
import episode
KEY=open(os.path.expanduser("~/.volcano/keys/groq"),encoding="utf-8").read().strip()
PH=["He's got decoys in play","It wasn't just lunch. It was fish and chips","We finally meet","I'm Eminem","Energy security is national security","Our enemies should be afraid","To be clear, you never saw combat","Hashtag commanders in beef is trending","Your presidency is in diapers","would you do me the honor","Surprised you didn't paint flames on the side of it","Now that is American exceptionalism in action","Being normal-ish","I've never seen your movies","A toy gun","Open fire","Yours is to survive","No phones","Enjoy living the rest of your life as a bird sanctuary","Guys like you. You know, Jim Strong","I picked the biggest tree","I'm not waiting ten years","We are now in control of Echelon","You vetted me","You know, Water Cobra","No, no, Canadians","Keep calm and carry on","I think I'm ready to write those memoirs now","Huge fan","tear at the very fabric of NATO","I'm the commander-in-chief","That feel safe enough for you","But he's America's nutter","I thought you were dead","respectfully, sir, no you're not","I died in that plane crash and this is hell","Stop saying Tripoli","The most romantic goddamn thing I've ever heard","Just tuck your chin to your chest","Withdrawing from this alliance","Hey, the chin thing kind of worked, huh","What do you think, I've lost a step","It's Bradshaw","Madam President, thanks for keeping my seat warm","It wasn't Bradshaw. It was Kirk","Easy. I just kept going","Don't go dying on me a third time, okay","Any other toys in this Batmobile","Take this, you bloody bastards","Hold it right there","You're not getting rid of us that easy","It's that I'm a better actor","Who's the action hero now, huh","I know, I lied. I've seen them all","How's that for Jim Strong","My country, my condiments"]
D=[b for b in episode.BLOCKS if b[0]=="D"]; assert len(D)==len(PH)
norm=lambda w: re.sub(r"[^a-z0-9']","",w.lower())
def asr(p):
    b="----x"+uuid.uuid4().hex; parts=[]
    for k,v in [("model","whisper-large-v3"),("response_format","verbose_json"),("temperature","0"),("language","en"),("timestamp_granularities[]","word"),("timestamp_granularities[]","segment")]:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode()); parts.append(open(p,"rb").read()); parts.append(f"\r\n--{b}--\r\n".encode())
    while True:
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions",data=b"".join(parts),headers={"Authorization":"Bearer "+KEY,"Content-Type":"multipart/form-data; boundary="+b,"User-Agent":"curl/8"}),timeout=120))
        except urllib.error.HTTPError as e:
            m=e.read().decode()[:200]; print("  ",e.code,m,flush=True)
            if e.code==429: time.sleep(30); continue
            raise
os.makedirs("dal",exist_ok=True); res={}
if os.path.exists("d_align.json"): res=json.load(open("d_align.json",encoding="utf-8"))
for i,(b,ph) in enumerate(zip(D,PH)):
    if str(i) in res: continue
    s=b[1]; w0=max(0,s-7); p=f"dal/{i:02d}.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(w0),"-t","15","-i","src.mp4","-vn","-ac","1","-ar","16000",p],check=True)
    r=asr(p); words=r.get("words",[])
    tgt=[norm(x) for x in ph.split() if norm(x)]; ws=[norm(w["word"]) for w in words]
    best=(0,None)
    for k in range(len(ws)):
        for L in range(max(1,len(tgt)-2),min(len(tgt)+3,len(ws)-k+1)):
            sc=difflib.SequenceMatcher(None,tgt,ws[k:k+L]).ratio()
            if sc>best[0]: best=(sc,(k,L))
    if best[1]:
        k,L=best[1]; st=w0+words[k]["start"]; en=w0+words[k+L-1]["end"]
        res[str(i)]={"score":round(best[0],2),"st":round(st,2),"en":round(en,2),"got":" ".join(w["word"] for w in words[k:k+L]),"old":s}
    else: res[str(i)]={"score":0,"old":s}
    print(i,res[str(i)],flush=True); json.dump(res,open("d_align.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
    time.sleep(3.2)
