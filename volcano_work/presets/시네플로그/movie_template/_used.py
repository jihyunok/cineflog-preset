import json,sys
U=[]
for p in (1,2,3,4):
    for w in json.load(open(f'part{p}/windows_dry.json',encoding='utf-8')):
        U.append((w['s'], w['s']+w['b']-w['a']))
U.sort()
def free(a,b):
    hit=[(x,y) for x,y in U if x<b+3 and y>a-3]
    return hit
for r in sys.argv[1:]:
    a,b=map(float,r.split('-'))
    h=free(a,b); print(r, 'FREE' if not h else 'used: '+', '.join(f'{x:.1f}-{y:.1f}' for x,y in h[:8]))
