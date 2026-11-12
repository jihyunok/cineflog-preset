# -*- coding: utf-8 -*-
"""토막 X 검사(11-07 33v2 대본 고치기): 옛 대본(_v1_script.py)에서 토막 X 의 SPAN 줄만 segX.py 의 LINES 로 바꾼 시험 대본을
_seg/wX/ 에서 plan_v9 --dry · script_check 로 돌리고, 토막 안 줄의 문제와 나레 조각(원본 시각 + 컷 설명)만 보여 준다.
사용: python D:/cine_work/ep33v2_콜래트럴/_seg/check.py X [--no-jev]"""
import ast, json, os, re, shutil, subprocess, sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
X = sys.argv[1]; NOJEV = "--no-jev" in sys.argv
WK = r"D:\cine_work\ep33v2_콜래트럴"; SEG = os.path.join(WK, "_seg"); T = os.path.join(SEG, "w" + X)
V9 = r"C:\Users\uere\volcano_work\presets\시네플로그\v9"
os.makedirs(T, exist_ok=True)
for f in ["ep.json", "lines.json", "scenes.txt", "black_src.npy", "src_sm.json", "src_band.npy", "shots.json"]:
    if not os.path.exists(os.path.join(T, f)): shutil.copy2(os.path.join(WK, f), T)
src = open(os.path.join(WK, "_v1_script.py"), encoding="utf-8").read()
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
g = {}; exec(open(os.path.join(SEG, f"seg{X}.py"), encoding="utf-8").read(), g)
k0, k1 = g["SPAN"]; lines = src.splitlines(keepends=True)
a = SE[k0].lineno - 1; b = SE[k1].lineno - 1 if k1 < len(SE) else [i for i, l in enumerate(lines) if l.strip() == "]"][-1]
body = g["LINES"].strip("\n") + "\n"
test = "".join(lines[:a]) + body + "".join(lines[b:])
open(os.path.join(T, "script.py"), "w", encoding="utf-8").write(test)
ns = {}; exec(test, ns); S2 = ns["S"]
nnew = len([n for n in ast.parse(body.replace("\n", "\n")).body]) if False else None
SE2 = [n.value for n in ast.parse(test).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
kk = [k for k, e in enumerate(SE2) if a + 1 <= e.lineno <= a + body.count("\n")]
K0, K1 = min(kk), max(kk)
# narr_en 을 글로: 옛 번호→글 + 토막 EN
ns1 = {}; exec(src, ns1); old_en = json.load(open(os.path.join(WK, "_v1_narr_en.json"), encoding="utf-8"))
t2e = {}; n = 0
for x in ns1["S"]:
    if x[0] == "N": n += 1; t2e[x[1]] = old_en.get(str(n), "")
t2e.update(g.get("EN", {}))
en = {}; n = 0; miss = []
for x in S2:
    if x[0] == "N":
        n += 1; en[str(n)] = t2e.get(x[1], "")
        if not en[str(n)]: miss.append(x[1][:30])
json.dump(en, open(os.path.join(T, "narr_en.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
if miss: print("영어 없음(EN 에 넣을 것):", miss)
r = subprocess.run([sys.executable, os.path.join(V9, "plan_v9.py"), "--dry"], cwd=T, capture_output=True, text=True, encoding="utf-8", errors="replace")
rep = open(os.path.join(T, "plan_report.txt"), encoding="utf-8").read().splitlines()
def ks(line): return [int(m) for m in re.findall(r"줄(\d+)", line)]
print(f"== 토막 {X}: 옛 줄 {k0}~{k1 - 1} → 시험 대본 줄 {K0}~{K1}")
print(rep[0])
mine = [l for l in rep if l.startswith(("✗", "△")) and any(K0 <= k <= K1 for k in ks(l))]
print(f"토막 안 문제·경고 {len(mine)}")
for l in mine: print(" ", l)
W = json.load(open(os.path.join(T, "windows_dry.json"), encoding="utf-8")); SH = json.load(open(os.path.join(T, "shots.json"), encoding="utf-8"))
def desc(t): return next((x for x in SH if x["s"] <= t < x["e"]), {}).get("desc", "")
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
print("── 토막 줄 화면(화면초 · 원본초 · 컷 설명)")
for k in range(K0, K1 + 1):
    x = S2[k]
    if x[0] == "ZONE": print(f"k{k} ZONE {x[1]}"); continue
    ws = [w for w in W if w.get("k") == k]
    head = f"k{k} {x[0]} " + (x[1][:60] if x[0] == "N" else (x[2][:40] if x[0] == "D" else f"A {x[1]}"))
    print(head)
    if x[0] in ("N", "A"):
        for w in ws:
            sl = (w["b"] - w["a"]) * 1.05; print(f"     {mm(w['a'])} ← 원본 {mm(w['s'])} | {desc(w['s'] + sl / 2)[:120]}")
    elif ws: print(f"     {mm(ws[0]['a'])} ← 원본 {mm(ws[0]['s'])}")
if not NOJEV:
    shutil.copy2(os.path.join(WK, "lines.json"), T)
    r = subprocess.run([sys.executable, os.path.join(V9, "prep", "script_check.py")], cwd=T, capture_output=True, text=True, encoding="utf-8", errors="replace")
    sc = open(os.path.join(T, "script_check.txt"), encoding="utf-8").read().splitlines()
    m2 = [l for l in sc if any(K0 <= k <= K1 for k in ks(l))]
    print(f"── script_check(제브) 토막 안 {len(m2)}")
    for l in m2: print(" ", l[:260])
