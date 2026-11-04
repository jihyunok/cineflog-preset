# -*- coding: utf-8 -*-
# plan --dry 에서 「자리 없음」 걸린 A(소리 장면) 줄과 「까만 화면」 A 줄을 뺀다 (10-27)
import ast, re
log = open("_plan_dry.log", encoding="utf-8").read()
ks = {int(k) for k in re.findall(r"✗ 줄(\d+) A ", log)} | {int(k) for k in re.findall(r"✗ 줄(\d+) 조각 [\d:.]+ 원본 [\d:.]+ 까만", log)}
src = open("script.py", encoding="utf-8").read(); L = src.split("\n")
E = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign)][0].elts
n = 0
for k in ks:
    ln = E[k].lineno - 1
    if L[ln].startswith('("A"'): L[ln] = "# (뺌·자리 없음/까만 10-27) " + L[ln]; n += 1
open("script.py", "w", encoding="utf-8").write("\n".join(L)); print("A 뺌", n)
