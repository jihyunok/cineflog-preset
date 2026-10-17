# -*- coding: utf-8 -*-
# 10-17 나레 빼기 — 대사가 이미 말해 주는 장면(강의: 장면이 설명하면 나레 삭제). 글 앞부분으로 찾는다.
import ast, re, shutil
DROP = [
"긴장을 풀려고 술을", "꼼꼼한 돔은 분 단위", "그래도 로마 풍경에", "그래도 지금은 마음껏 즐기자며",
"이 말이 계속 마음에 걸리는", "황당한 오해에도, 창밖", "두 사람은 허둥지둥, 최대한 쿨하고", "그리고 두 사람의 영상이 정말 좋았다고",
"통화를 끊은 두 사람은, 한참", "길이 이상하다는 콜에게", "혼자 남은 콜은, 여기서 죽겠다며", "그리고 자리가 부족하니 사슴",
"말은 안 통하지만, 할머니는 두 사람을 집 안으로", "그런데 돔이 뭔가를 알아챕니다", "그런데 키스를 하자, 할머니가",
"분위기가 풀리자, 두 사람은 아까", "어머니가 중요한 손님이니", "프란체스카는 두 사람이 누군지", "마시모는 지오반니도 게이였다고",
"콜은 숨어 있는 돔을 감추려고", "정당방위였다며 서로를 달래", "의사를 불러 달라는 마시모", "얼굴의 피를 허겁지겁", "어디냐는 질문엔, 피자를",
"약혼자가 쓰러진 걸 본 그녀에게", "그 사이 돔은 엉뚱한 열쇠만", "튀어나온 염소를 피하려다", "표를 사는데, 직원이",
"돔은 자기가 다 뒤집어쓸 테니", "정말 날 두고 가려 했냐는", "결국 상담 예약부터", "그리고 부모가 되기 위해 어디까지 할 수 있냐고",
]
shutil.copy("script.py", "script_v4_repair.py")
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
