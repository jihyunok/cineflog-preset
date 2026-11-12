# -*- coding: utf-8 -*-

# autowiden.py — plan 「자리 없음」 줄 구간 넓힘 + 막는 이웃 대사 빼기
import json as _json, os as _os
_W = _json.load(open("_widen.json", encoding="utf-8")) if _os.path.exists("_widen.json") else {}
S = [(("N", x[1]) + tuple(_W[x[1]]) + tuple(y for y in x[2:] if isinstance(y, dict))) if x[0] == "N" and x[1] in _W else x for x in S]
_D = _json.load(open("_drop.json", encoding="utf-8")) if _os.path.exists("_drop.json") else []
S = [x for x in S if not (x[0] == "D" and x[2] in _D)]
# 11-04 녹음 뒤 빼는 나레(앞뒤 대사 3초 간격에 막혀 자리 없음 → 대사끼리 이어도 뜻이 통함) — 빼면 renum.py 로 번호 다시
_DN = []
S = [x for x in S if not (x[0] == "N" and x[1] in _DN)]
# (녹음 뒤 길이가 모자라면 여기에 _ADD — ep35_추룡/_post_merge.py 견본, 이름표·noflip 앞에)
# 11-01 이름표 시트: 뒤통수·얼굴 가린 컷 → 얼굴 보이는 줄(_tag_moves.json, 최종 S 인덱스) + 반전 빼기(_noflip_k.json)
def _setd(x, upd, drop=()):
    d = next((y for y in x[2:] if isinstance(y, dict)), None)
    base = tuple(y for y in x if not isinstance(y, dict))
    nd = {k: v for k, v in (d or {}).items() if k not in drop}
    nd.update(upd)
    return base + ((nd,) if nd else ())
# 11-05 4차: 번호(S 인덱스)로 적은 _tag_moves.json·_noflip_k.json 은 대본 줄이 늘고 줄면 엉뚱한 줄에 붙는다 →
#   글(나레 글 / 대사 자막)로 적은 _tag_moves_txt.json·_noflip_txt.json 이 있으면 그것을 쓴다(번호 파일은 옛 기록으로 남김)
def _txt(x): return x[1] if x[0] == "N" else (x[2] if x[0] == "D" else f"A{x[1]}")
if _os.path.exists("_tag_moves_txt.json"):
    _ix = {_txt(x): k for k, x in enumerate(S) if x[0] != "ZONE"}
    for _m in _json.load(open("_tag_moves_txt.json", encoding="utf-8")):
        if _m["from"] in _ix: S[_ix[_m["from"]]] = _setd(S[_ix[_m["from"]]], {}, ("tag", "tag_w"))
        if _m["to"] in _ix: S[_ix[_m["to"]]] = _setd(S[_ix[_m["to"]]], _m["tag"], ("tag", "tag_w"))
        else: print("이름표 옮길 줄 없음", _m["to"])
elif _os.path.exists("_tag_moves.json"):
    for _m in _json.load(open("_tag_moves.json", encoding="utf-8")):
        S[_m["from"]] = _setd(S[_m["from"]], {}, ("tag", "tag_w"))
        S[_m["to"]] = _setd(S[_m["to"]], _m["tag"], ("tag", "tag_w"))
if _os.path.exists("_noflip_txt.json"):
    _ix = {_txt(x): k for k, x in enumerate(S) if x[0] != "ZONE"}
    for _t in _json.load(open("_noflip_txt.json", encoding="utf-8")):
        if _t in _ix: S[_ix[_t]] = _setd(S[_ix[_t]], {"noflip": True})
        else: print("noflip 줄 없음", _t)
elif _os.path.exists("_noflip_k.json"):
    for _k in _json.load(open("_noflip_k.json", encoding="utf-8")):
        S[_k] = _setd(S[_k], {"noflip": True})
# 손으로 고치기: ("nocont", None) = 핵심 장면 이음 풀기 · ("rng", [(a,b),...]) = 구간 바꾸기
_FIX = {
    "배 안에선, 사진 속 그 여자가 아트를 기다립니다.": ("rng", [(4690.9, 4698.6)]),  # 11-05 편집자 통독 — 위 줄 새 글
    "계획대로 붙잡힌 아트는, 제네시스호에서 가드너와 마주하죠.": ("rng", [(4690.9, 4698.6)]),  # 11-05 토막3 끝 조각과 3초 간격
}
for _k, _x in enumerate(S):
    if _x[0] == "N" and _x[1] in _FIX:
        _how, _v = _FIX[_x[1]]
        _d = next((y for y in _x[2:] if isinstance(y, dict)), None)
        if _how == "nocont":
            S[_k] = _setd(_x, {}, ("cont",)) if _d else _x
        else:
            S[_k] = (("N", _x[1]) + (tuple(_v[0]) if len(_v) == 1 else (_v,))) + ((_d,) if _d else ())
