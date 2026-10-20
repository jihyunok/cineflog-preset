# -*- coding: utf-8 -*-
# 10-17 14v2 나레 빼기 — 대사가 이미 말해 주는 장면(강의: 장면이 설명하면 나레 삭제). 글 앞부분으로 찾는다.
import ast, re, shutil
DROP = [
"하지만 바닥에 엎드리라는", "둘은 몇 주년인지를", "게다가 중간에 쉬지 않으려고", "배너는 경비원쯤은", "결혼기념일 같은 건 자신에겐",
"트래비스가 받은 훈련은", "왜 경찰이 되려 하냐는", "부하들이 당했으니", "함께하면 살고", "이미 해고된 트래비스는",
"그래도 트래비스는 겁나서", "그리고 조이에게, 남편을", "경보를 울리면 러셀은", "조이가 함께 가자고", "아내 이름을 어떻게",
"트래비스는 러셀이 곧 퇴직", "트래비스는 러셀이 영화 속", "조이는 전화를 받고 적당히", "보안요원들은 향수", "러셀은 처음 본 여자에게",
"내털리는 기념일을 망쳤다며", "트래비스는 러셀에게 사랑한다며",
]
shutil.copy("script.py", "script_v3_repair.py")
src = open("script.py", encoding="utf-8").read(); lines = src.splitlines(keepends=True)
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
hit = set()
for e in SE:
    if isinstance(e, ast.Tuple) and e.elts[0].value == "N":
        t = e.elts[1].value
        for d in DROP:
            if t.startswith(d): lines[e.lineno - 1] = ""; hit.add(d)
print("뺀 나레", len(hit), "· 못 찾음", [d for d in DROP if d not in hit])
open("script.py", "w", encoding="utf-8").write("".join(lines))
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
print("N", sum(1 for x in ns["S"] if x[0] == "N"), "chars", sum(len(re.sub(r"\s", "", x[1])) for x in ns["S"] if x[0] == "N"))
