# -*- coding: utf-8 -*-
# 대작 03 v3 — v2 대본에서 흐름 끊긴 곳만 고친다(나머지 그대로)
# 10-20 텔레그램 "5분55초에서 갑자기 다른장면이 바뀌면서 인물소개도 없고 왜 간건지도 모르겠어. 확인해. 그리고 남자친구가 왜 교도소를 들어가게 된건지 전환이 너무 빨라 이해도가 떨어져."
#  · "이 영화뿐 아니라 다음영화에서도 이런일이 일어나지 않게 확인하고 규칙을 정해." → flow_check.py · cold_read.py 로 찾은 곳
# 입력 script_v2.py(v2 그대로 보관) → script.py · emph.json · narr_en.json · narr/(글이 같은 녹음은 번호만 옮김) · 새로 녹음할 줄
import glob, json, os, shutil
if not os.path.exists("script_v2.py"):
    shutil.copy2("script.py", "script_v2.py"); shutil.copy2("emph.json", "emph_v2.json"); shutil.copy2("narr_en.json", "narr_en_v2.json")
    if os.path.exists("narr") and not os.path.exists("narr_v2"): shutil.copytree("narr", "narr_v2")
src = open("script_v2.py", encoding="utf-8").read(); ns = {}; exec(src, ns); S = list(ns["S"])
def opt(x): return dict(x[-1]) if isinstance(x[-1], dict) else {}
def base(x): return tuple(x[:-1]) if isinstance(x[-1], dict) else tuple(x)
def find(pred):
    ks = [k for k, x in enumerate(S) if pred(x)]
    assert len(ks) == 1, ("못 찾음/여럿", ks); return ks[0]
def N(t): return lambda x: x[0] == "N" and x[1] == t
def D(ids): return lambda x: x[0] == "D" and (x[1] if isinstance(x[1], list) else [x[1]]) == ids
def A(a): return lambda x: x[0] == "A" and abs(x[1] - a) < 0.01
def put(pred, *new): k = find(pred); S[k:k + 1] = list(new)
def retext(t, nt, rng=None):
    k = find(N(t)); b = list(base(S[k])); b[1] = nt
    if rng is not None: b = b[:2] + (list(rng) if isinstance(rng, tuple) else [rng])
    o = opt(S[k]); S[k] = tuple(b) + ((o,) if o else ())
def tag(pred, tg, drop=False):
    k = find(pred); o = opt(S[k])
    if drop: o.pop("tag", None); o.pop("tag_w", None)
    else: o["tag"] = tg
    S[k] = base(S[k]) + ((o,) if o else ())

# ① 5:55 도서관 → 시스터 집: 대사 「그땐 제가 착각했나 봐요」로 바로 넘어가던 곳 — 왜 갔는지 나레로 열고, 스프락 이름표
put(D([381]), ("N", "얼마 뒤, 놀러 오라던 시스터의 집을 찾아갑니다.", 1373.8, 1382.6))
put(A(1368.9))                                                          # 도서관 혼자 컷(2초)은 빼고 나레가 3초 간격 안에 들어가게
tag(D([388, 389, 390]), ["스프락", "시스터의 남자친구"])
# ② 윌리 잭 체포: 「주머니엔 218달러」 한 줄 → 경찰 대사로 이유(2시간 전 편의점 도난 신고 + 14살)를 살리고 나레로 정리
#   (대사 창은 3초까지라 경찰 설명 대사(6.6초)는 못 씀 → 나레가 이유를 말하고, 「열 넷이요」 뒤 체포 나레)
retext("난데없이 들이닥친 경찰이, 소녀의 나이를 묻는데,", "알고 보니 2시간 전 도난 신고된 돈과 담배. 게다가 경찰은 소녀의 나이를 묻는데,", (1062.5, 1080.4))
put(D([306]))                                                           # 「주머니엔 218달러」 자리까지 나레가 써야 3초 간격 안에 들어감(나레가 「졸렌이 내민 돈」을 받음)
#   체포 장면은 원래 소리 장면(A) 그대로 두고, 감옥 장면 첫 나레에서 이유를 한 번 더
retext("한편 윌리 잭은 철창 신세가 됐는데", "한편 장물에 미성년자까지, 윌리 잭은 철창행.", (1162.0, 1174.5))
put(D([324]))                                                           # 감방 동료 「이봐, 예쁜이」 뜬금 한마디 — 나레 자리
# ③ 렉시 이름표는 처음 소개하는 줄에(나중 줄에 달려 있었음)
tag(N("살가운 간호사 렉시의 손길."), ["렉시", "간호사"])
tag(N("그날 밤 아기를 받아 준 사람이 누구였는지, 렉시가 들려주는데,"), None, drop=True)
# ④ 시상식 → 윌리 잭 모텔: 장소가 아예 바뀌어 다른 줄거리 → 「한편」
retext("윌리 잭은 낯선 여자와 뒤엉켜 방에 들어서는데, 침대 위엔 루스가,", "한편 윌리 잭은 낯선 여자와 뒤엉켜 방에 들어서는데, 침대 위엔 루스가,", [(4473.0, 4490.0), (4496.5, 4500.2)])
# (cold_read 로 찾은 곳은 아래에 이어서)
exec(open("_mk_v3_more.py", encoding="utf-8").read()) if os.path.exists("_mk_v3_more.py") else None

head = src.split("S = [")[0].replace("_mk_v2.py 가 만든다 — 대작 03 v2(나레만 출발 비디오여행식)", "_mk_v3.py 가 만든다 — 대작 03 v3(v2 + 흐름 끊긴 곳 고침)")
open("script.py", "w", encoding="utf-8").write(head + "S = [\n" + "".join(repr(x) + ",\n" for x in S) + "]\n")
# 번호 옮기기 — 나레 번호(n001~)가 밀리므로 글 기준으로
old_N = [x[1] for x in ns["S"] if x[0] == "N"]; new_N = [x[1] for x in S if x[0] == "N"]
e2 = json.load(open("emph_v2.json", encoding="utf-8")); n2 = json.load(open("narr_en_v2.json", encoding="utf-8"))
be = {old_N[int(i) - 1]: v for i, v in e2["n"].items()}; bn = {old_N[int(i) - 1]: v for i, v in n2.items()}
if os.path.exists("narr_en_add.json"): bn.update(json.load(open("narr_en_add.json", encoding="utf-8")))   # 새 줄 영어(제브 나레↔그림용)
emph = dict(e2, n={}); en = {}
for i, t in enumerate(new_N, 1):
    if t in be: emph["n"][str(i)] = be[t]
    if t in bn: en[str(i)] = bn[t]
json.dump(emph, open("emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(en, open("narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
have = {}
for d in ("narr_v2", "narr_new_rec"):
    for p in sorted(glob.glob(d + "/n*.json")):
        t = json.load(open(p, encoding="utf-8"))["text"]
        if t not in have: have[t] = p
shutil.rmtree("_narr_new", ignore_errors=True); os.makedirs("_narr_new"); rec = []
for i, t in enumerate(new_N, 1):
    p = have.get(t)
    if not p: rec.append((i, t)); continue
    shutil.copy2(p[:-5] + ".wav", f"_narr_new/n{i:03d}.wav"); shutil.copy2(p, f"_narr_new/n{i:03d}.json")
if os.path.exists("narr"): shutil.rmtree("narr")
os.rename("_narr_new", "narr")
json.dump(rec, open("_rec_v3.json", "w", encoding="utf-8"), ensure_ascii=False)
print("S", len(S), "· 나레", len(new_N), "(v2", len(old_N), ") · 녹음 다시 씀", len(new_N) - len(rec), "· 새로 녹음", len(rec), "줄", sum(len(t) for _, t in rec), "자")
for i, t in rec: print(f"  n{i:03d} {t}")
