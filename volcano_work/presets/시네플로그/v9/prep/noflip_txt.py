# -*- coding: utf-8 -*-
"""11-05 48 프로젝트 파워: 반전 빼기를 줄 번호가 아니라 **글 기준**(_noflip_txt.json — 나레 글 / 대사 자막 / A조각은 "A<시작초>")으로 유지.
대본을 고친 뒤 plan_v9.py(실제) → 이 파일 → _merge.py → plan_v9.py 다시. 기존 목록 + text_sec.tsv(영어 글자 초) 에 걸린 조각 + 핵심 장면 이음(cont) 앞뒤를 묶음.
_post_merge.py 는 _noflip_txt.json·_tag_moves_txt.json 이 있으면 그것을 쓴다(견본: 수정용 ep48_프로젝트파워/_post_merge.py). 사용: 작업 폴더에서 python noflip_txt.py"""
import json,sys
sys.stdout.reconfigure(encoding="utf-8")
ns={};exec(open('script.py',encoding='utf-8').read(),ns);S=ns['S']
W=json.load(open('windows.json',encoding='utf-8'))
prev=set(json.load(open('_noflip_txt.json',encoding='utf-8')))
txt=set()
for l in open('text_sec.tsv',encoding='utf-8'):
    p=l.split('\t')
    if p and p[0].strip().isdigit(): txt.add(int(p[0]))
def T(x): return x[1] if x[0]=='N' else (x[2] if x[0]=='D' else f"A{x[1]}")
need=set()
for w in W:
    s=w['s']; e=s+(w['b']-w['a'])*w.get('rate',1)*1.05
    if any(int(s)<=t<=e for t in txt): need.add(w['k'])
for k,x in enumerate(S):
    if x[0]=='ZONE': continue
    if T(x) in prev: need.add(k)
    if isinstance(x[-1],dict) and x[-1].get('noflip'): need.add(k)
for k,x in enumerate(S):
    if x[0]=='N' and isinstance(x[-1],dict) and x[-1].get('cont'):
        grp=[k-1,k,k+1]
        if any(g in need for g in grp): need.update(grp)
out=sorted({T(S[k]) for k in need if 0<=k<len(S) and S[k][0]!='ZONE'})
json.dump(out,open('_noflip_txt.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(out))
