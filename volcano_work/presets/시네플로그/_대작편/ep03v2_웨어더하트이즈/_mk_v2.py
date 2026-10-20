# -*- coding: utf-8 -*-
# 대작 03 v2 대본 만들기 — 10-20 텔레그램 "아니~ 전체적으로 수정해서 만들어. 이정도면 된것같아."
# = 롱폼 03 script.py 의 S 그대로(대사·소리 장면·그림·noflip) + 나레 글만 출발 비디오여행식으로:
#   훅 S1~S9·본편 S99~·아웃트로 = 서브에이전트 4명 결과(_out_w1~4.json, 지시 _v2_지시.md) · 앞부분 S11~S98 = 사용자가 OK 한 견본(ep03n_…_나레견본/script.py) 그대로.
# 결과: script.py · emph.json · narr_en.json · narr/(글이 같은 녹음은 다시 씀) · 새로 녹음할 줄 목록
import glob, json, os, re, shutil
HERE = os.getcwd(); LF = "../ep03_웨어더하트이즈"; SM = "../ep03n_웨어더하트이즈_나레견본"
def load_S(d):
    os.chdir(d); ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); os.chdir(HERE); return ns["S"]
S0 = load_S(LF); SS = load_S(SM)
OUT = {}
for p in sorted(glob.glob("_out_w*.json")): OUT.update(json.load(open(p, encoding="utf-8")))
def opt_of(x): return dict(x[-1]) if isinstance(x[-1], dict) else {}
def base_of(x): return x[:-1] if isinstance(x[-1], dict) else x
S = []; tagged = {"노블리", "윌리 잭", "모지스", "시스터 허즈번드"}; miss = []
def take(k, x):
    if x[0] != "N": return x
    o = OUT.get(f"S{k}")
    if not o: miss.append(k); return x
    b = list(base_of(x)); b[1] = o["text"]; op = opt_of(x)
    if o.get("tag") and o["tag"] not in tagged:
        op["tag"] = [o["tag"], o["tag_rel"]] if o.get("tag_rel") else o["tag"]; tagged.add(o["tag"])
    return tuple(b) + ((op,) if op else ())
for k in range(0, 11): S.append(take(k, S0[k]))          # 훅 + ZONE main
S += SS[1:]                                               # 견본(사용자 OK) — S11~S98 자리
# 견본 두 줄은 실제 녹음 길이에 맞춰 그림 구간만 손봄(글은 그대로)
for i, x in enumerate(S):
    if x[0] == "N" and x[1].startswith("트레일러촌의 열일곱 살"): S[i] = (x[0], x[1], [(40.7, 43.3), (47.3, 49.92)]) + x[3:]
    if x[0] == "N" and x[1].startswith("평생 바퀴 달린 집에서만"): S[i] = (x[0], x[1], [(186.3, 189.4), (179.4, 182.8), (173.3, 176.5)]) + x[3:]
for k in range(99, len(S0)): S.append(take(k, S0[k]))     # 본편 나머지 + 아웃트로
head = open("_head.py", encoding="utf-8").read().split("\n", 1)[1]
# 실제 녹음 길이에 맞춰 그림 구간만 손봄(10-20 plan: 3초 간격에 끼인 줄)
for i, x in enumerate(S):
    if x[0] == "N" and x[1] == "버티고 버티다 결국 바닥에 털썩.": S[i] = (x[0], x[1], [(1629.5, 1634.4), (1637.5, 1641.0)]) + x[3:]
    if x[0] == "N" and x[1] == "그때 불쑥 찾아온 친엄마 마마 릴.": S[i] = (x[0], x[1], [(1977.4, 1979.2), (1980.9, 1983.68)]) + (dict(x[-1], tag_w=1),)
    if x[0] == "N" and x[1] == "시큰둥하더니 결국 어니와 결혼합니다.": S[i] = (x[0], x[1], 6047.2, 6055.0) + x[4:]
    if x[0] == "A" and tuple(x[1:4]) == (6055.0, 6060.0, 2.5): S[i] = ("A", 6058.0, 6063.0, 2.5) + x[4:]
    if x[0] == "N" and x[1].startswith("아기 침대 앞에서 한참을"): S[i] = (x[0], x[1], 958.2, 971.0) + x[4:]        # 관문 ⑨: 첫 조각이 화분 든 컷 → 아기 침대 컷부터
    if x[0] == "N" and "메리 엘리자베스" in x[1]: S[i] = (x[0], x[1], [(2896.6, 2899.2), (2874.0, 2883.0)]) + x[4:]   # 둘째 조각이 벼룩시장 → 누나가 보이는 침실 컷만
open("script.py", "w", encoding="utf-8").write("# -*- coding: utf-8 -*-\n# _mk_v2.py 가 만든다 — 대작 03 v2(나레만 출발 비디오여행식)\n" + head + "\nS = [\n" + "".join(repr(x) + ",\n" for x in S) + "]\n")
# 강조·영어: 견본은 견본 파일에서(글 기준), 나머지는 서브에이전트 결과에서
N = [x for x in S if x[0] == "N"]
se = json.load(open(f"{SM}/emph.json", encoding="utf-8")); sn = json.load(open(f"{SM}/narr_en.json", encoding="utf-8"))
sm_N = [x[1] for x in SS if x[0] == "N"]
by_text_emph = {sm_N[int(i) - 1]: v for i, v in se["n"].items() if int(i) <= len(sm_N)}
by_text_en = {sm_N[int(i) - 1]: v for i, v in sn.items() if int(i) <= len(sm_N)}
for o in OUT.values():
    if o.get("emph"): by_text_emph[o["text"]] = o["emph"]
    if o.get("en"): by_text_en[o["text"]] = o["en"]
le = json.load(open(f"{LF}/emph.json", encoding="utf-8"))
emph = {"why": "10-20 대작 03 v2 — 지무비식 자막 강조(나레 번호 → [말, 감정])", "n": {}, "dlg_yellow": le.get("dlg_yellow", [])}
en = {}
for i, x in enumerate(N, 1):
    e = by_text_emph.get(x[1])
    if e and e[0] and e[0] in x[1]: emph["n"][str(i)] = e
    if x[1] in by_text_en: en[str(i)] = by_text_en[x[1]]
json.dump(emph, open("emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(en, open("narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
# 녹음: 글이 같은 조각을 찾아 새 번호로
have = {}
for d in ("narr", f"{SM}/narr", f"{SM}/_b1", f"{SM}/_b2", f"{SM}/_b3", f"{LF}/narr"):
    for p in sorted(glob.glob(d + "/n*.json")):
        t = json.load(open(p, encoding="utf-8"))["text"]
        if t not in have: have[t] = p
shutil.rmtree("_narr_new", ignore_errors=True); os.makedirs("_narr_new"); rec = []
for i, x in enumerate(N, 1):
    src = have.get(x[1])
    if not src: rec.append((i, x[1])); continue
    shutil.copy2(src[:-5] + ".wav", f"_narr_new/n{i:03d}.wav"); shutil.copy2(src, f"_narr_new/n{i:03d}.json")
if os.path.exists("narr"): shutil.rmtree("narr")
os.rename("_narr_new", "narr")
print("S", len(S), "· 나레", len(N), "· 결과 없는 줄", miss, "· 이름표", sorted(tagged), "· 강조", len(emph["n"]), "· 영어", len(en), "/", len(N))
print("녹음 다시 씀", len(N) - len(rec), "· 새로 녹음", len(rec), "줄", sum(len(t) for _, t in rec), "자")
