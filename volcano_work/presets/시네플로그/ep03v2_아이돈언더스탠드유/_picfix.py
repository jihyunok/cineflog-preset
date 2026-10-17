# -*- coding: utf-8 -*-
# 10-17 그림 대조(review_n) 뒤 고침 — 나레 밑 그림이 문장과 어긋난 곳
import ast, json, shutil
shutil.copy("script.py", "script_pre_picfix_1017.py")
src = open("script.py", encoding="utf-8").read(); lines = src.splitlines(keepends=True)
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
ns = {}; exec(src, ns); S = ns["S"]
def kN(prefix):
    r = [k for k, x in enumerate(S) if x[0] == "N" and x[1].startswith(prefix)]; assert len(r) == 1, (prefix, r); return r[0]
def kD(ids):
    r = [k for k, x in enumerate(S) if x[0] == "D" and x[1] == ids]; assert len(r) == 1, (ids, r); return r[0]
def put(k, s): lines[SE[k].lineno - 1] = s + "\n"
def drop(k): lines[SE[k].lineno - 1] = ""
def setN(prefix, a, b, text=None, opt=""):
    k = kN(prefix); t = text or S[k][1]
    put(k, f'("N", {json.dumps(t, ensure_ascii=False)}, {a}, {b}{opt}),')
setN("결혼 10년 차 부부, 돔과 콜.", 37.0, 47.5); drop(kD([2, 3]))                   # 0:31 크레딧 화면 → 소개 영상
setN("아기를 낳을 엄마 캔디스에게", 50.0, 67.0)
setN("말이 안 통하는 두 미국인에겐", 3792.0, 3808.0)                               # 마당의 프란체스카 빼기
setN("콜의 칼에는 철자가 틀린 쿨", 515.0, 521.0, "철자가 틀린 쿨. 이 칼, 꼭 기억하세요.", ', {"noflip": True}'); drop(kD([264]))
setN("다음 날, 렌터카를 받은", 738.5, 752.0)                                         # 앞 장면(밤 다리) 빼기
setN("그날 저녁, 드디어 10주년", 1244.0, 1312.0)
setN("15년 동안 고기를 끊었던 콜은", 2268.0, 2292.0)
setN("그런데 결국, 콜의 속이", 2405.0, 2418.0)
k = kN("캄캄한 부엌에서 허둥대던"); put(k, '("N", "캄캄한 부엌에서 콜과 부딪힌 할머니가, 지하실 계단 아래로 굴러떨어집니다.", 2716.0, 2746.0),')
drop(kN("할머니는 그대로 지하실 계단"))
setN("마시모가 술을 가지러 간 사이", 3512.0, 3530.0)
setN("우릴 죽이려던 사람이니", 4268.0, 4300.0)
setN("차에 올라탄 프란체스카는", 4439.0, 4462.0, "헛간에 숨은 프란체스카는, 도끼를 들고 두 사람에게 욕을 퍼붓습니다.")
setN("그리고 어둠 속에서, 차가 프란체스카를", 4462.0, 4500.0, "그리고 어둠 속, 달아나던 프란체스카가 차와 부딪히고 맙니다.")
setN("공항에 도착한 두 사람은", 5013.0, 5030.0)
k = kN("블랙 코미디 스릴러, 아이 돈 언더스탠드 유였습니다"); i = SE[k].lineno - 1
lines[i] = lines[i].replace("[(298.0, 306.0), (5430.0, 5445.0)]", "[(301.6, 306.0), (5430.0, 5445.0)]")
open("script.py", "w", encoding="utf-8").write("".join(lines))
print("ok")
