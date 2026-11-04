# -*- coding: utf-8 -*-
"""plan --dry 에서 「자리 없음」 걸린 나레 줄만 script_v8_before_np.py 의 원래 구간으로 되돌린다. 사용: python _np_revert.py  (_plan_dry.log 읽음)"""
import json, re
log = open("_plan_dry.log", encoding="utf-8").read()
ks = sorted({int(k) for k in re.findall(r"✗ 줄(\d+) ", log)})
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
L = open("script.py", encoding="utf-8").read().split("\n"); O = open("script_v8_before_np.py", encoding="utf-8").read().split("\n")
done = []
for k in ks:
    x = S[k]
    if x[0] != "N": continue
    pre = '("N", ' + json.dumps(x[1], ensure_ascii=False) + ","
    a = [i for i, l in enumerate(L) if l.startswith(pre)]; b = [l for l in O if l.startswith(pre)]
    if len(a) == 1 and len(b) == 1 and L[a[0]] != b[0]: L[a[0]] = b[0]; done.append(k)
open("script.py", "w", encoding="utf-8").write("\n".join(L))
print("되돌림", done, "· 나레 아닌 줄", [k for k in ks if S[k][0] != "N"])
