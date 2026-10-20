# -*- coding: utf-8 -*-
# 본편(main) 줄 순서 검사: 원본 시각이 앞 줄보다 3초 넘게 거꾸로 가는 줄
import json
L={x["id"]:x for x in json.load(open("lines.json",encoding="utf-8"))}
ns={}; exec(open("script.py",encoding="utf-8").read(),ns); S=ns["S"]
def st(x):
    if x[0]=="D": return min(L[i]["ws"] for i in x[1]), max(L[i]["we"] for i in x[1])
    if x[0]=="A": return x[1], x[2]
    r=x[2] if isinstance(x[2],(list,tuple)) else [(x[2],x[3])]
    return r[0][0], r[-1][1]
zone=None; prev=None
for k,x in enumerate(S):
    if x[0]=="ZONE": zone=x[1]; prev=None; continue
    if zone!="main": continue
    a,b=st(x)
    if prev and a < prev[1]-3 and a < prev[0]:
        print(k, x[0], round(a,1), "<", prev[2], round(prev[0],1), "|", str(x[1])[:30], "‖ 앞:", str(S[prev[3]][1])[:30])
    prev=(a,b,S[k][0],k)
