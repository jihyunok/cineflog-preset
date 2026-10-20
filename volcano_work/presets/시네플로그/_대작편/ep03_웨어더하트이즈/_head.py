# -*- coding: utf-8 -*-
import json as _json
_L = {x["id"]: x for x in _json.load(open("lines.json", encoding="utf-8"))}
_K = {}
for _r in open("srt.txt", encoding="utf-8"):
    _p = _r.rstrip("\n").split("\t")
    if len(_p) >= 3: _K[int(_p[0])] = (float(_p[1]), float(_p[2]))
def sr(*idx):
    """자막 번호들이 덮는 시각과 겹치는 원본 대사 줄 id"""
    a = min(_K[i][0] for i in idx); b = max(_K[i][1] for i in idx)
    return [x["id"] for x in _L.values() if x["s"] < b - 0.15 and x["e"] > a + 0.15]
