# -*- coding: utf-8 -*-
# (prep/reorder.py, 05v2 10-18) 본편에서 원본 시각이 앞 나레 구간보다 앞선 D/A 줄을 그 나레 앞으로 옮긴다(이야기 순서 = 원본 순서) — 10-18
import ast, json
L={x["id"]:x for x in json.load(open("lines.json",encoding="utf-8"))}
src=open("script.py",encoding="utf-8").read()
lines=src.split("\n")
T=ast.parse(src); SE=[n.value for n in T.body if isinstance(n,ast.Assign) and getattr(n.targets[0],"id","")=="S"][0].elts
ns={}; exec(src,ns); S=ns["S"]
def st(x):
    if x[0]=="D": return min(L[i]["ws"] for i in x[1])
    if x[0]=="A": return x[1]
    r=x[2] if isinstance(x[2],(list,tuple)) else [(x[2],x[3])]
    return r[0][0]
# 줄 번호(0기준) 목록과 내용
items=[(e.lineno-1, S[k]) for k,e in enumerate(SE)]
order=[i for i,_ in items]
zone=None; moves=0
seq=[]  # (line_idx, item, zone)
for (li,x) in items:
    if x[0]=="ZONE": zone=x[1]
    seq.append([li,x,zone])
changed=True
while changed:
    changed=False
    for j in range(1,len(seq)):
        li,x,z=seq[j]; pli,px,pz=seq[j-1]
        if z!="main" or pz!="main" or x[0] not in ("D","A") or px[0]!="N": continue
        if st(x) < st(px)-0.5:
            seq[j-1],seq[j]=seq[j],seq[j-1]; changed=True; moves+=1
new=list(lines)
slots=[li for li,_,_ in sorted(seq,key=lambda s:s[0])]
for slot,(li,x,z) in zip(slots,seq): new[slot]=lines[li]
open("script.py","w",encoding="utf-8").write("\n".join(new))
print("옮김", moves)
