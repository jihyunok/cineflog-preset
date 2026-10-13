# 나레 블록마다 그 장면 원본 구간에서 짧은 대사 1~2개를 골라 후보로 뽑는다
import json,glob,re,episode
segs=[]
for p in sorted(glob.glob("t/*.json")):
    segs+=json.load(open(p,encoding="utf-8"))
segs=[x for x in segs if x["t"] and "BF" not in x["t"]]
for i in range(len(segs)): segs[i]["e"]=segs[i+1]["s"] if i+1<len(segs) else segs[i]["s"]+3
DF=json.load(open("d_final.json",encoding="utf-8"))
res=[(d["s"]-0.5,d["s"]+d["d"]+0.5) for d in DF]
def ok(s,e): return all(e+3.2<=a or s>=b+3.2 for a,b in res)
bad=re.compile(r"thank you|♪|🎵|music|\.\.\.$",re.I)
N=[]; bi=0
for k,b in enumerate(episode.BLOCKS):
    if b[0]!="N": continue
    bi+=1
    nd=json.load(open(f"narr/n{bi:02d}.json",encoding="utf-8")); ndur=nd["en"][-1]
    want=2 if ndur>14 else 1
    if k<3: want=0            # 훅 첫 15초는 나레만
    a,bb=b[2],b[3]; got=[]
    for pad in (0,20,45):
        cands=[x for x in segs if a-pad<=x["s"]<=bb+pad and x not in got]
        cands=[x for x in cands if 2<=len(x["t"].split())<=11 and 0.9<=x["e"]-x["s"]<=4.2 and not bad.search(x["t"]) and ok(x["s"],x["e"])]
        cands.sort(key=lambda x:(-(x["t"].strip()[-1:] in "?!"), abs(x["e"]-x["s"]-2.2)))
        for x in cands:
            if len(got)>=want: break
            if ok(x["s"],x["e"]): got.append(x); res.append((x["s"]-0.5,x["e"]+0.5))
        if len(got)>=want: break
    for x in sorted(got,key=lambda x:x["s"]): N.append({"blk":k,"ni":bi,"s":x["s"],"e":x["e"],"en":x["t"].strip()})
json.dump(N,open("d2_cands.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
print(len(N))
