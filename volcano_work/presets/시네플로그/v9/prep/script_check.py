# -*- coding: utf-8 -*-
"""대본 단계 검사 (11-07 33 콜래트럴 박제 — 녹음 전에 0 까지): 작업 폴더에서
 ① 결과 먼저 문장: 나레 문장이 사건의 결과(쓰러집니다·떠납니다·이깁니다·뒤집어 버리죠·방아쇠를 당깁니다…)를 말하는데
    바로 뒤에 그 장면 대사가 이어지면(다음 대사 원본이 그 문장 구간 끝에서 90초 안) — 그 대사 뒤로 옮기거나 「~하려는 순간」으로.
    판정은 제브(_제브/나레_결과문장.json: reports_outcome·spoils_next), 제브가 안 되면 낱말 목록. 예외: 그 나레 줄 {"result_ok": "이유"}.
 ② 같은 내용 나레 연달아: 이웃 나레 두 줄(다음·다다음)을 제브(_제브/나레_되풀이.json repeats) + 글자 겹침으로 — 경고.
사용: python script_check.py [--th 0.6] → script_check.txt · 걸린 ① 이 있으면 exit 1
문턱 0.7(reports_outcome) = 33 콜래트럴 옛 대본으로 잼: 분석이 찾은 결과 먼저 문장 10개 모두 0.72~0.91, 결과 아닌 문장은 0.62 아래.
 spoils_next(대사가 할 말을 나레가 먼저)는 참고로만 적는다. ② 되풀이 문턱 0.85 = 분석이 찾은 연달아 4쌍(섬 사진·트렁크·가방·피버) 0.85~0.95."""
import argparse, json, os, re, subprocess, sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
JEV = os.path.expanduser(r"~/volcano_work/_제브")
ap = argparse.ArgumentParser(); ap.add_argument("--th", type=float, default=0.7); ap.add_argument("--rep", type=float, default=0.85); ap.add_argument("--no-jev", action="store_true")
A = ap.parse_args()
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
EN = json.load(open("narr_en.json", encoding="utf-8")) if os.path.exists("narr_en.json") else {}
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
def ssplit(t): return [x.strip() for x in re.split(r"(?<=[.?!…])\s+", t.strip()) if x.strip()]
KW = re.compile(r"쓰러집|쓰러지고|쓰러뜨|떠납니다|떠나 버|떠나죠|뒤집어|뒤집힙|이깁니다|이기죠|이겨 냅|당깁니다|당기죠|죽습니다|죽고 말|숨을 거|숨집니다|사살|체포됩|체포되|붙잡힙|떨어집니다|추락합|맞혀 내|알아보지 못|달아납니다|도망칩니다|빠져나갑|성공합|실패합|들통|발각|끝내 |결국 ")
rows = []; zone = "main"; ni = 0; N = []
for k, x in enumerate(S):
    if x[0] == "ZONE": zone = x[1]; continue
    opt = x[-1] if isinstance(x[-1], dict) else {}
    if x[0] == "N":
        ni += 1; rs = x[2] if isinstance(x[2], (list, tuple)) else [(x[2], x[3])]
        # 문장 칸이 [(a1,b1),(a2,b2)](한 문장 속 동작 여럿)이면 그 문장 구간 = 처음~끝
        rs = [(min(float(q[0]) for q in r), max(float(q[1]) for q in r)) if isinstance(r[0], (list, tuple)) else (float(r[0]), float(r[1])) for r in rs]
        N.append(dict(k=k, ni=ni, text=x[1], zone=zone, opt=opt, a=min(a for a, _ in rs), b=max(b for _, b in rs), rs=rs))
    elif x[0] == "D" and N:
        ids = x[1] if isinstance(x[1], list) else [x[1]]
        s = min(L[i]["ws"] for i in ids if L[i]["ws"] is not None)
        N[-1].setdefault("next_d", []).append(dict(k=k, s=s, ko=x[2], en=" / ".join(L[i]["en"] for i in ids)))
items = []; cand = []
for n in N:
    if n["zone"] == "outro": continue
    ks = ssplit(n["text"]); es = ssplit(EN.get(str(n["ni"]), ""))
    if len(es) != len(ks): es = [EN.get(str(n["ni"]), "")] * len(ks)
    nd = n.get("next_d", [])
    for q, (ko, en) in enumerate(zip(ks, es)):
        r = n["rs"][q] if n["opt"].get("sent") and q < len(n["rs"]) else (n["a"], n["b"])
        near = [d for d in nd if d["s"] - r[1] < 90]          # 그 문장 구간 끝에서 90초 안에 시작하는 뒤 대사 = 같은 장면으로 본다
        c = dict(id=f"n{n['ni']:03d}_q{q}", k=n["k"], ni=n["ni"], ko=ko, en=en or ko, r=r, near=near, kw=bool(KW.search(ko)), ok=n["opt"].get("result_ok"))
        cand.append(c)
        items.append({"id": c["id"], "line": c["en"], "next_dialogue": " | ".join(d["en"] for d in nd[:4]) or "(no dialogue follows)"})
pairs = []
for i, x in enumerate(N):
    for y in N[i + 1:i + 3]:
        if y["zone"] != x["zone"]: continue
        pairs.append({"id": f"r{x['ni']:03d}_{y['ni']:03d}", "first": EN.get(str(x["ni"]), x["text"]), "second": EN.get(str(y["ni"]), y["text"])})
def jev(spec, its, tag):
    if A.no_jev: return None
    fi, fo = f"_sc_{tag}_in.jsonl", f"_sc_{tag}_out.jsonl"
    with open(fi, "w", encoding="utf-8") as f:
        for it in its: f.write(json.dumps(it, ensure_ascii=False) + "\n")
    if os.path.exists(fo): os.remove(fo)
    r = subprocess.run(["py", "-3.12", rf"{JEV}\거르기.py", "--spec", rf"{JEV}\{spec}", "--in", fi, "--out", fo], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.exists(fo): print("제브 실패 — 낱말 목록으로:", (r.stdout + r.stderr)[-300:]); return None
    out = {j["id"]: j["answers"] for j in map(json.loads, open(fo, encoding="utf-8"))}
    if len(out) < len(its): print(f"제브 {len(its) - len(out)}건 빠짐 — 빠진 건 낱말 목록으로")
    return out
J = jev("나레_결과문장.json", items, "res"); JR = jev("나레_되풀이.json", pairs, "rep")
T = []; hard = 0
def bg(s): s = re.sub(r"[\s.,!?…'\"“”‘’]", "", s); return {s[i:i + 2] for i in range(len(s) - 1)}
T.append(f"# 대본 검사 — 나레 {len(N)}줄 · 문장 {len(cand)} · 제브 {'씀' if J else '못 씀(낱말 목록)'} · 문턱 {A.th}")
for c in cand:
    a = (J or {}).get(c["id"])
    pr = a["reports_outcome"] if a else (1.0 if c["kw"] else 0.0)
    if pr < A.th or not c["near"]: continue
    d0 = c["near"][0]
    tag = f"(예외: {c['ok']})" if c["ok"] else "✗"
    if not c["ok"]: hard += 1
    T.append(f"{tag} ① 줄{c['k']} n{c['ni']:03d} 결과 문장 「{c['ko']}」 (제브 결과 {a['reports_outcome']:.2f}·스포 {a['spoils_next']:.2f}) 구간 {mm(c['r'][0])}~{mm(c['r'][1])} → 바로 뒤 대사 줄{d0['k']} 원본 {mm(d0['s'])} 「{d0['ko'][:30]}」 — 대사 뒤로 옮기거나 「~하려는 순간」" if a else
             f"{tag} ① 줄{c['k']} n{c['ni']:03d} 결과 낱말 「{c['ko']}」 → 뒤 대사 줄{d0['k']} 원본 {mm(d0['s'])}")
rep = 0
for p in pairs:
    x, y = int(p["id"][1:4]), int(p["id"][5:8]); X = next(n for n in N if n["ni"] == x); Y = next(n for n in N if n["ni"] == y)
    a = (JR or {}).get(p["id"]); A_, B_ = bg(X["text"]), bg(Y["text"]); j = len(A_ & B_) / max(1, min(len(A_), len(B_)))
    if (a and a["repeats"] >= A.rep) or j >= 0.45:
        rep += 1; T.append(f"△ ② 같은 내용 연달아? 줄{X['k']} 「{X['text'][:34]}」 ↔ 줄{Y['k']} 「{Y['text'][:34]}」 (제브 {a['repeats'] if a else '-'} · 글자 겹침 {j:.2f})")
T.append(f"결과 먼저 문장 {hard} · 같은 내용 연달아 {rep}")
open("script_check.txt", "w", encoding="utf-8").write("\n".join(T) + "\n"); print("\n".join(T))
json.dump(dict(res=J, rep=JR), open("_sc_scores.json", "w", encoding="utf-8"), ensure_ascii=False)
sys.exit(1 if hard else 0)
