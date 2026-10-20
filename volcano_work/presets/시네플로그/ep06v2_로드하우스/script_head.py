# -*- coding: utf-8 -*-
# 06 로드 하우스 다시 만들기 대본 (10-17, 사용자 "저거 다 엉망이야 다시만들어야해" + "다운로드에 새로운 영화원본있어 끝나는 작업계속해줘").
# 옛 06(10-02) 대본을 _convert.py 로 옮긴 뒤 03v2 처럼 다듬는다. 벤치 시네마톡 D8wDpJZYaUQ(300만)은 이야기 흐름 길잡이만. ★결말·에필로그까지.
# 가장 기본: ("N", 나레, a, b) 의 [a,b] = 그 문장이 말하는 바로 그 장면. 강의: 3초 쓰고 3초 건너뛰기 · 나레 1 : 영상 2.
# ("D", sr(자막번호…), "우리 자막") — srt.txt(공식 한국어 자막, 끝 「자막: 민선호」 한 줄 뺀 번호 — 1546번까지는 옛 06 번호 그대로) 시각의 원본 대사 줄(lines.json). ("A", a, b, 길이) — 소리만 살린 장면.
# ★가게 이름이 영화 제목과 같다 — 본편 나레는 「술집·가게」. 1:54:40 쯤부터 엔딩 크레딧, 그 사이 녹스가 병원에서 깨어나 달아나는 장면(6800~6870)까지 넣는다(결말까지).
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
S = [
("ZONE", "hook"),
