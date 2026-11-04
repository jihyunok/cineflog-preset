# -*- coding: utf-8 -*-

# autowiden.py — plan 「자리 없음」 줄 구간 넓힘 + 막는 이웃 대사 빼기
import json as _json, os as _os
_W = _json.load(open("_widen.json", encoding="utf-8")) if _os.path.exists("_widen.json") else {}
S = [(("N", x[1]) + tuple(_W[x[1]]) + tuple(y for y in x[2:] if isinstance(y, dict))) if x[0] == "N" and x[1] in _W else x for x in S]
_D = _json.load(open("_drop.json", encoding="utf-8")) if _os.path.exists("_drop.json") else []
S = [x for x in S if not (x[0] == "D" and x[2] in _D)]
# (녹음 뒤 길이가 모자라면 여기에 _ADD — ep35_추룡/_post_merge.py 견본, 이름표·noflip 앞에)
# 11-01 이름표 시트: 뒤통수·얼굴 가린 컷 → 얼굴 보이는 줄(_tag_moves.json, 최종 S 인덱스) + 반전 빼기(_noflip_k.json)
def _setd(x, upd, drop=()):
    d = next((y for y in x[2:] if isinstance(y, dict)), None)
    base = tuple(y for y in x if not isinstance(y, dict))
    nd = {k: v for k, v in (d or {}).items() if k not in drop}
    nd.update(upd)
    return base + ((nd,) if nd else ())
if _os.path.exists("_tag_moves.json"):
    for _m in _json.load(open("_tag_moves.json", encoding="utf-8")):
        S[_m["from"]] = _setd(S[_m["from"]], {}, ("tag", "tag_w"))
        S[_m["to"]] = _setd(S[_m["to"]], _m["tag"], ("tag", "tag_w"))
if _os.path.exists("_noflip_k.json"):
    for _k in _json.load(open("_noflip_k.json", encoding="utf-8")):
        S[_k] = _setd(S[_k], {"noflip": True})
