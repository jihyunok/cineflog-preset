# -*- coding: utf-8 -*-
"""지무비식 자막 꼴 표 — build_v9.py(ASS) 와 ../capcut_font.py(캡컷)가 같이 읽는다(한 곳).
10-16 04v2 위드아웃 리모스 사용자 "글자가 내가새로준 지침에 보면 큰글자도있고 색깔있는글자도 있고 다양한데 넌 그걸안지켰네?"
출처: 영화리뷰롱폼 엔진(presets/영화리뷰롱폼/엔진/longmovie/pipeline/builders) text_layout.TONE_FONT·ROLE_FONT·FONTS_EXTRA·JIMOVIE_INK,
caption_stream FLAT_RED/LIME/ORANGE/YELLOW·그라데 5쌍. 글꼴 파일은 이 컴퓨터 font_resolution 의 대체 글꼴(산돌 → 눈누/OFL)."""

# 엔진 글꼴 키 → (작업 폴더 fonts/ 파일, ASS 글꼴 이름, 글꼴 크기 100 일 때 잉크 높이)
# ★ASS 이름은 글꼴 파일 name ID 1·4(정식 이름) — ID 16(묶음 이름)을 쓰면 libass 가 못 찾고 기본 글꼴로 그린다(10-16 견본).
#   본명조는 「Noto Serif KR」(전체 이름 「… Bold」는 못 찾음) · 청도읍성체는 이름의 괄호 「CHEONGDO(M)」 를 \fn 이 못 읽어
#   name 표만 바꾼 사본 CheongdoM-renamed.ttf(fontTools)를 쓴다.
JM_FONTS = {
    "본명조": ("NotoSerifKR-Bold.otf", "Noto Serif KR", 100), "네모니2오블리크": ("AstaSans-ExtraBold.ttf", "Asta Sans ExtraBold", 88),
    "네모니2정자": ("GoyangDeogyang-Bold.ttf", "GoyangDeogyang", 95), "격동명조": ("MBC1961M.ttf", "MBC 1961 Medium", 85),
    "코믹스텐실": ("KBLCourt_EB.ttf", "KBL Court EB TTF", 92), "광화문": ("Yeonil_TM.ttf", "Yeonil_TM", 93),
    "광야": ("EunpyeongSagaDogseoTitle-Regular.ttf", "EunpyeongSagaDogseo Title", 93), "카리스마": ("TTBookendBatangSB.ttf", "Bookend Batang SemiBold", 96),
    "액션스텐실": ("WandocleanseaB.ttf", "Wandocleansea Bold", 95), "성경": ("KimjungchulScript-Bold.ttf", "Kim jung chul Script Bold", 98),
    "아침": ("Eulyoo1945-SemiBold.ttf", "Eulyoo1945 SemiBold", 97), "방각본": ("CheongdoM-renamed.ttf", "CheongdoM", 93),
    "카페24당당해": ("Cafe24Dangdanghae.ttf", "Cafe24 Dangdanghae", 90)}
# 감정 → (글꼴 키, 색 RGB, 기울임) — TONE_FONT · NAR_ALT_FONT(아침·성경). 색 None = 그라데 5쌍 순환(ASS 는 그라데가 없어 진한 쪽 단색)
JM_TONE = {
    "grad_slant": ("네모니2오블리크", None, 1), "reveal": ("네모니2정자", (254, 231, 0), 0), "threat": ("격동명조", (247, 1, 8), 0),
    "money": ("광야", (85, 219, 77), 0), "twist": ("코믹스텐실", (251, 77, 33), 0), "climax": ("액션스텐실", (247, 1, 8), 0),
    "kill": ("카리스마", (247, 1, 8), 0), "woodcut": ("방각본", (247, 106, 24), 0), "emotion": ("아침", (254, 231, 0), 0)}
JM_GRAD = [(253, 140, 50), (250, 70, 70), (254, 200, 40), (60, 220, 250), (120, 230, 60)]
# 잉크 높이(px, 1080p) — plain = 사장님 b29 카페24당당해 58px(소형 나레) · emph/punch = JIMOVIE_INK nar_emph/punch · dlg = config ink_px.dlg
# ★10-20 대작 03 v3 사용자 "캐릭터들이 말할때 자막 조금 더 크게 해줘" → dlg 54 → 66(약 1.2배), 노란 대사(dlg_y 90)는 그대로
JM_INK = {"plain": 52, "emph": 118, "punch": 158, "dlg": 66, "dlg_y": 90}
JM_W = 1700                       # 한 줄 폭 상한(text_layout.K_WIDTH nar)
JM_WHITE = (252, 253, 253)
JM_NAME2FILE = {v[1]: v[0] for v in JM_FONTS.values()}
