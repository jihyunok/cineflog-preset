# -*- coding: utf-8 -*-
"""33v3 4차 토막 준비 — v3 1차 굽기 대본을 기준으로 남은 P 줄을 토막 a·b 로 나눔(11-12)."""
import csv, json, ast, os, shutil
WK = r'D:\cine_work\ep33v3_콜래트럴'; SEG = os.path.join(WK, '_seg4'); os.makedirs(SEG, exist_ok=True)
src = open(os.path.join(WK, 'script.py'), encoding='utf-8').read(); ns = {}; exec(src, ns); S = ns['S']
ni2k = {}; n = 0
for k, x in enumerate(S):
    if x[0] == 'N': n += 1; ni2k[n] = k
B = ni2k[55]
for f, t in [('script.py', '_base_script.py'), ('narr_en.json', '_base_narr_en.json'), ('emph.json', '_base_emph.json')]:
    shutil.copy2(os.path.join(WK, f), os.path.join(SEG, t))
SE = [nd.value for nd in ast.parse(src).body if isinstance(nd, ast.Assign) and getattr(nd.targets[0], 'id', '') == 'S'][0].elts
L = src.splitlines(keepends=True); end_i = [i for i, l in enumerate(L) if l.strip() == ']'][-1]
spans = {'a': (0, B), 'b': (B, len(S))}
rows = list(csv.DictReader(open(r'D:\cine_work\재검사_1107\ep33v3_후\줄별_화면판정_1차.csv', encoding='utf-8-sig')))
amb = {'75': '판정자: 말한 사람 빈센트는 보이나 입을 연 쪽은 맥스 — P 여지', '71': '판정자: 설명 대상(죽은 남자) 직접 안 보임 — 꾸밈말로 O',
       '135': '판정자: 맥스가 두 프레임 모두 입 다묾 — P 여지', '204': '판정자·본체: 쓰러진 경찰과 겨눈 총 손잡이, 맥스 얼굴 안 보임 — P 여지',
       '203': '판정자: 노트북 장면이 바로 앞이라 지난 일로 O'}
T3 = open(os.path.join(WK, '_seg3', 'BRIEF3.md'), encoding='utf-8').read()
why = ("## 왜\n사용자(11-11) 「95프로로 올려」. v2 재검사 76.3% → 3차 작업자 3명이 고친 v3 1차 굽기를 새 판정자 3명이 다시 보니 "
       "**맞음 229/244(93.9%) · 부분 15 · 어긋남 0** — 95%(232줄)에 3줄 모자란다.\n"
       "이번 4차는 남은 P 15줄만(토막 a·b 둘). 여유를 두려고 이 토막 P 줄을 **거의 다** O 로 만든다. 3차에서 이미 한 번 손본 줄이 많다 — "
       "기준 대본 줄 끝 주석과 `D:\\cine_work\\ep33v3_콜래트럴\\_seg3\\seg*.py` 의 CHANGES 를 보면 무엇을 해 봤는지 안다.\n"
       "이번 판은 엔진 밀림이 이미 없다(몸통 = 계획 1259.92초). 시트의 시작 프레임은 그 자막 줄 시작 +0.1초 = 완성본 그대로다. "
       "완성본 `D:\\cine_work\\ep33v3_콜래트럴\\final.mp4`, 판정 시트 `D:\\cine_work\\재검사_1107\\ep33v3_후\\sheets\\`.\n"
       "먼저 읽어라: 1차 지시 `D:\\cine_work\\ep33v3_콜래트럴\\_seg\\BRIEF.md`(대본 꼴·규칙) · 판정 기준 "
       "`C:\\Users\\uere\\volcano_work\\presets\\시네플로그\\v9\\판정지시_틀.md`.\n\n")
for X, (k0, k1) in spans.items():
    a = SE[k0].lineno - 1; b = SE[k1].lineno - 1 if k1 < len(SE) else end_i
    open(os.path.join(SEG, f'seg{X}.py'), 'w', encoding='utf-8').write(
        f"# 33v3 4차 토막 {X} — 기준 대본(_seg4/_base_script.py = v3 1차 굽기 대본) 줄 {k0}~{k1 - 1} 을 이 LINES 로 바꾼다(11-12). 처음엔 기준 줄 그대로.\n"
        f"SPAN = ({k0}, {k1})\nLINES = r'''\n{''.join(L[a:b])}'''\nEN = {{}}\nEMPH = {{}}\nCHANGES = []\n")
    K = []
    for r in rows:
        k = ni2k[int(r['blk'])]
        if not (k0 <= k < k1): continue
        if r['verdict'] != 'O':
            K.append(f"- 줄{k}(n{int(r['blk']):03d}) 자막 #{r['idx']} 완성본 {r['start']} 원본 {r['src1']}·{r['src2']} 「{r['text']}」 — v3 1차 판정 {r['verdict']}: {r['note']}")
        elif r['idx'] in amb:
            K.append(f"- (경계 — 지금 O, 깨지지 않게만 · 쉽게 더 확실해지면 고쳐도 됨) 줄{k}(n{int(r['blk']):03d}) 자막 #{r['idx']} 완성본 {r['start']} 「{r['text']}」 — {amb[r['idx']]}: {r['note'][:160]}")
    T = T3.replace('_seg3', '_seg4').replace('check3', 'check4').replace('BRIEF3', 'BRIEF4')
    i0 = T.index('## 왜'); i1 = T.index('## 판정 기준')
    T = T[:i0] + why + T[i1:]
    T = T.replace('목표: 이 토막 P·X 줄의 **5/6 이상을 O 로**.', '목표: 이 토막 P 줄을 **거의 다 O 로**(못 고치면 이유).')
    open(os.path.join(SEG, f'BRIEF4_{X}.md'), 'w', encoding='utf-8').write(T.replace('{X}', X).replace('{KNOWN}', '\n'.join(K)))
    print(X, k0, k1, len(K))
c3 = open(os.path.join(WK, '_seg3', 'check3.py'), encoding='utf-8').read()
c3 = c3.replace('"_seg3"', '"_seg4"').replace('_seg3/check3.py', '_seg4/check4.py').replace('(11-12 33v3 — v2 대본 + 본체 5줄 고친 _base_script.py 기준', '(11-12 33v3 4차 — v3 1차 굽기 대본 기준')
open(os.path.join(SEG, 'check4.py'), 'w', encoding='utf-8').write(c3)
m3 = open(os.path.join(WK, '_seg3', 'merge3.py'), encoding='utf-8').read()
m3 = m3.replace('"_seg3"', '"_seg4"').replace('for X in "abc":', 'for X in "ab":').replace('33v3: 글로 새 번호에 옮김', '33v3 4차: 글로 새 번호에 옮김')
open(os.path.join(SEG, 'merge4.py'), 'w', encoding='utf-8').write(m3)
