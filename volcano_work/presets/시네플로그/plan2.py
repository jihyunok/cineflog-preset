# 지무비식 구성: 나레를 문장마다 끊고 문장 뒤마다 원본 대사 1개
import json,glob,re,episode
REMOVE={13,16,19,26,38,51,64,75,98,107,115,132,147,162,165,178,186,197}
HOOK={0,1,2}; OUTRO={202,203,204}
DF=json.load(open("d_final.json",encoding="utf-8")); D2=json.load(open("d2_final.json",encoding="utf-8"))
# 기존 대사를 블록에 붙인다
att={}; di=0; last_n=None
for k,b in enumerate(episode.BLOCKS):
    if b[0]=="N":
        if k not in REMOVE: last_n=k
    else:
        d=dict(DF[di]); di+=1; att.setdefault(last_n,[]).append(d)
for d in D2:
    k=d["blk"]
    while k in REMOVE: k-=1
    while episode.BLOCKS[k][0]!="N" or k in REMOVE: k-=1
    att.setdefault(k,[]).append(dict(d))
used=[(d["s"],d["s"]+d["d"]) for v in att.values() for d in v]
segs=[]
for p in sorted(glob.glob("t/*.json")): segs+=json.load(open(p,encoding="utf-8"))
segs=[x for x in segs if x["t"]]
for i in range(len(segs)): segs[i]["e"]=segs[i+1]["s"] if i+1<len(segs) else segs[i]["s"]+3
bad=re.compile(r"thank you|♪|🎵|BF|\bsaint\b|hang me|volare|wise men|falling in love",re.I)
def good(x):
    t=x["t"].strip(); w=t.split(); d=x["e"]-x["s"]
    return 2<=len(w)<=9 and 0.8<=d<=3.4 and t[-1:] in ".?!" and t[:1].isupper() and not bad.search(t)
def free(s,e): return all(e+3.1<=a or s>=b+3.1 for a,b in used)
plan=[]; ni=0; need=0
for k,b in enumerate(episode.BLOCKS):
    if b[0]!="N": continue
    ni+=1
    if k in REMOVE: continue
    js=json.load(open(f"narr/n{ni:02d}.json",encoding="utf-8")); ch=js["chars"]
    ends=[i for i,c in enumerate(ch[:-1]) if c in ".?!"]
    cuts=[0.0]
    for i in ends:
        t=(js["en"][i]+js["st"][i+1])/2
        if t-cuts[-1]>=2.6 and js["en"][-1]-t>=2.6: cuts.append(t)
    cuts.append(None)
    pieces=[(cuts[i],cuts[i+1]) for i in range(len(cuts)-1)]
    mine=sorted(att.get(k,[]),key=lambda d:d["s"])
    for pi,(a,e) in enumerate(pieces):
        plan.append({"type":"N","blk":k,"ni":ni,"a":a,"e":e,"rng":[b[2],b[3]]})
        if k in HOOK or k in OUTRO: continue
        if mine: plan.append({"type":"D",**mine.pop(0)}); continue
        # 새 대사 후보
        got=None
        for pad in (0,25,60):
            for x in segs:
                if b[2]-pad<=x["s"]<=b[3]+pad and good(x) and free(x["s"]-0.3,x["e"]):
                    got=x; break
            if got: break
        if got:
            used.append((got["s"]-0.3,got["e"])); need+=1
            plan.append({"type":"D","new":True,"s":got["s"],"e":got["e"],"en":got["t"].strip(),"ko":""})
    for d in mine: plan.append({"type":"D",**d})      # 남은 기존 대사
json.dump(plan,open("plan2.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
N=[p for p in plan if p["type"]=="N"]; D=[p for p in plan if p["type"]=="D"]
print("pieces",len(N),"dialogues",len(D),"new",need)
