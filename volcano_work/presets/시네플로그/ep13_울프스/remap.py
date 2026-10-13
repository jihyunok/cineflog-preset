"""나레 조각을 빼거나 살린 뒤 addev.json 의 조각 번호(ni)를 새 대본에 맞춘다: python remap.py 옛모듈 새모듈"""
import json, sys, importlib
def m(S):
    r = {}; ni = 0; pos = 0
    for x in S:
        if x[0] == "R": continue
        pos += 1
        if x[0]: ni += 1
        r[pos] = ni
    return r
A, B = (importlib.import_module(n).S for n in sys.argv[1:3])
a, b = m(A), m(B); o2p = {}
for p, n in a.items(): o2p.setdefault(n, p)
old = json.load(open("addev.json")); new = {}
for k, v in old.items(): new.setdefault(str(b[o2p[int(k)]]), []).extend(v)
json.dump(new, open("addev.json", "w"), indent=0)
