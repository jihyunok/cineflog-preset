# -*- coding: utf-8 -*-
"""★11-07 훅 첫 10초 서명 — prep/hookcheck.py(시트·hook_check.json 만듦)와 gate.py ⑯(사람이 채운 것 확인)이 같이 쓴다.
windows.json 의 앞 10초 조각(a·b·s·반전 여부)이 바뀌면 서명이 바뀌어 옛 확인은 무효."""
import hashlib, json

HOOK_SEC = 10.0

def hook_windows(W):
    return [w for w in W if w["a"] < HOOK_SEC]

def sig(W):
    x = [[round(w["a"], 3), round(w["b"], 3), round(w["s"], 3), bool(w.get("noflip"))] for w in hook_windows(W)]
    return hashlib.sha1(json.dumps(x).encode("utf-8")).hexdigest()
