# -*- coding: utf-8 -*-
# 10-17 자동 대사(dauto) 자막 다듬기 — 그 창에서 실제로 하는 말만(옆 줄 섞인 것 빼기), 뜻 안 맞는 줄은 뺌
import ast, json, shutil
shutil.copy("script.py", "script_pre_dtext_1017.py")
T = {28: "잡생각 잊기 좋겠어 / 재밌을 거야", 29: "응 / 10분쯤 있으면 오실 거야", 53: "세상에! / 미안해요",
     59: "저도 이거랑 / 똑같은 거 있어요", 67: None, 72: "기념일엔 오르비에토에 / 있을 거라며? / 네",
     76: "정말 고마워요", 83: "차오, 차오 / 그럴게요", 91: None, 96: None, 115: "두 분 되게 / 재밌어 보여요",
     130: "고마워요 / 두 분, 진짜 좋아요", 151: "그렇지? / 그랬을 거 같아", 226: "맛있어 보인다 / 고맙습니다",
     242: "아빠가 못 될 수도 / 있겠다고", 247: "진짜 신나는 파티거든!", 276: "네? / 잘했어!",
     307: "집 전화 써 / 집 전화?", 373: "어머니가 / 너무 기뻐하세요", 375: "먹으러…? / 함께 식사하러요 / 네",
     395: "저희 이제 갈게요", 400: "엄마가 동생 셔츠를 / 줬다고요?", 409: None, 414: None,
     420: "저 안에 / 숨었나 봐요", 434: "그 사람… / 모르겠어", 444: None,
     448: "듀오링고 효과가 / 슬슬 나오네 / 발음 좋았어, 자기", 451: None, 459: "부재중 전화가… / 정말 미안해요",
     465: "기분은 어때요? / 다 괜찮아요", 477: "내가 열쇠 찾을게 / 잠깐만, 기다려요!", 493: "그러다 염소가…",
     512: None, 521: "이따가 맬게 / 오늘 사고만 몇 번이야", 549: None}
src = open("script.py", encoding="utf-8").read(); lines = src.splitlines(keepends=True)
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
for k, t in T.items():
    e = SE[k]; i = e.lineno - 1
    assert e.elts[0].value == "D" and "dauto" in lines[i], (k, lines[i])
    if t is None: lines[i] = ""; continue
    seg = ast.get_source_segment(src, e.elts[2]); lines[i] = lines[i].replace(seg, json.dumps(t, ensure_ascii=False), 1)
open("script.py", "w", encoding="utf-8").write("".join(lines))
print("ok", len(T))
