import json, re, shutil, sys, os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
D='G:/내 드라이브/'
V=Path('C:/Users/uere/Documents/쇼츠업로더영상')
OK="사용자 11-02 「드라마채널들 … 내일 영상도 각각올려줘」"
def sec(t,name):
    m=re.search(r'\['+name+r'\][^\n]*\n(.*?)(?=\n\[|\Z)',t,re.S); return m.group(1).strip() if m else ''
jobs=[]
for ch,n in [('드라마법사','악의꽃'),('재미지니','나의해피엔드'),('대박드라마8898','이상한변호사우영우')]:
    t=open(f'{D}다시나레/{n}_업로드.txt',encoding='utf-8').read()
    c1=re.search(r'\n1\.\s*(.+?)(?:\s*\(0\.\d+\))?\n',t).group(1)
    title=re.sub(r'\s*《.*$','',c1).strip()          # 사용자 11-02 올린 꼴: 《작품》 이하 뺌
    desc=sec(t,'설명').split('\n')
    tags_line=desc[0]
    body=[l for l in desc if l and not l.startswith('#') and not l.startswith('📺') and not l.startswith('---')]
    syn=[]
    for l in body:
        if l.startswith('▶'): break
        syn.append(l)
    d='\n'.join(syn)+'\n'+tags_line
    dst=V/ch; dst.mkdir(parents=True,exist_ok=True)
    f=dst/f'{n}_몰아보기_새나레.mp4'
    if not f.exists(): shutil.copy2(f'{D}다시나레/{n}_몰아보기_새나레.mp4',f)
    shutil.copy2(f'{D}다시나레/{n}_썸네일보기_1.jpg',f.with_suffix('.jpg'))
    jobs.append(dict(channel=ch,file=str(f),title=title,desc=d,tags=[],made_for_kids=False,category=24,approved_by=OK,approved_on='2026-11-02'))
# 시네플로그 27 사마리탄
s=f'{D}영화리뷰/27_사마리탄/시네플로그/'
t=open(s+'27_사마리탄_업로드.txt',encoding='utf-8').read()
title=sec(t,'제목').split('\n')[0]
d=sec(t,'설명'); tags=[x.strip() for x in sec(t,'태그').split(',') if x.strip()]
dst=V/'시네플로그'; dst.mkdir(parents=True,exist_ok=True)
f=dst/'27_사마리탄.mp4'
if not f.exists(): shutil.copy2(s+'27_사마리탄.mp4',f)
shutil.copy2(s+'27_사마리탄_썸네일보기_1_와반전소름돋음.jpg',f.with_suffix('.jpg'))
jobs.append(dict(channel='시네플로그',file=str(f),title=title,desc=d,tags=tags,made_for_kids=False,category=22,approved_by=OK,approved_on='2026-11-02'))
json.dump(jobs,open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False,indent=1)
for j in jobs: print(j['channel'],'|',j['title'],'|',len(j['desc']),os.path.getsize(j['file'])//2**20,'MB', os.path.getsize(Path(j['file']).with_suffix('.jpg'))//1024,'KB'); print(j['desc'][:300]); print()
