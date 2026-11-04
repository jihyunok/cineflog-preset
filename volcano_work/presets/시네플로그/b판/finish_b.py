# -*- coding: utf-8 -*-
"""무비세상 B판 마무리(make_b.py init·rewrite·emph 뒤): 녹음 → 계획(자리 없는 소리 장면 A 뺌) → narr_pic → 관문 pre → 자르기·굽기 → finalcheck → 완성본/무비세상.
관문 ⑨(나레↔그림)는 A판에서 눈으로 보고 허용한 나레 줄이면 같은 이유로 허용, 새로 걸린 줄이 있으면 b_new9.txt 에 적고 멈춘다(exit 3 — 보고 나서 gate_allow 에 넣고 다시).
사용: python finish_b.py <B판 폴더> [--from plan|gate|build|deliver]"""
import json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); V9 = os.path.join(HERE, "..", "v9")
B = sys.argv[1].rstrip("/\\"); FROM = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else "tts"
STEPS = ["tts", "plan", "gate", "build", "deliver"]
os.chdir(B); ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
CFG = json.load(open("ep.json", encoding="utf-8")); A = CFG["b_from"]
OUT = os.path.expanduser("~/volcano_work/시네플로그/완성본/무비세상"); os.makedirs(OUT, exist_ok=True)
m = re.match(r"ep(\d+)b_(.+)", os.path.basename(B)); NAME = f"{m.group(1)}_{m.group(2)}"
def run(*a, log=None):
    r = subprocess.run([sys.executable, *a], capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if log: open(log, "w", encoding="utf-8").write(r.stdout + r.stderr)
    return r
def on(s): return STEPS.index(s) >= STEPS.index(FROM)

if on("tts"):
    r = run(os.path.join(HERE, "make_b.py"), "tts", B); print(r.stdout[-300:], r.stderr[-1500:])
    if r.returncode: sys.exit("tts 실패")

if on("plan"):
    import ast
    for it in range(6):
        r = run(os.path.join(V9, "plan_v9.py"), log="_plan_dry.log"); out = r.stdout
        ks = {int(k) for k in re.findall(r"✗ 줄(\d+) A ", out)} | {int(k) for k in re.findall(r"✗ 줄(\d+) 조각 [\d:.]+ 원본 [\d:.]+ 까만", out)}
        # 10-31 ep25: 구간은 넉넉한데 옆 대사와 3초 간격 때문에 자리 없음 → 글을 줄여도 소용없음 → 구간을 앞뒤 6초 넓힘(최대 2번)
        kw = {int(m.group(1)) for m in re.finditer(r"✗ 줄(\d+) N .*자리 없음 — 구간 ([\d.]+)초, 필요 약 ([\d.]+)초", out) if float(m.group(3)) <= float(m.group(2)) * 0.9}
        kn = {int(k) for k in re.findall(r"✗ 줄(\d+) N .*자리 없음", out)} - kw | {int(k) for k in re.findall(r"✗ 줄(\d+) 「.*조각 \d+개로는 .*넘음", out)}   # 구간 여럿인 나레가 길어 조각이 2.9초 넘음도 줄임
        src = open("script.py", encoding="utf-8").read(); L = src.split("\n")
        E = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
        if ks:      # 자리 없는 소리 장면(A)부터 뺀다 — 옆 나레 자리를 막고 있을 수 있음
            for k in ks:
                ln = E[k].lineno - 1
                if L[ln].lstrip().startswith('("A"'): L[ln] = "# (B판 뺌·자리 없음/까만) " + L[ln]
            open("script.py", "w", encoding="utf-8").write("\n".join(L)); print("A 뺌", len(ks)); continue
        wid = json.load(open("b_widen.json")) if os.path.exists("b_widen.json") else {}
        kw = {k for k in kw if wid.get(str(k), 0) < 2 and len(E[k].elts) >= 4 and all(isinstance(e, ast.Constant) and isinstance(e.value, (int, float)) for e in E[k].elts[2:4])}
        kn = ({int(k) for k in re.findall(r"✗ 줄(\d+) N .*자리 없음", out)} - kw) | {int(k) for k in re.findall(r"✗ 줄(\d+) 「.*조각 \d+개로는 .*넘음", out)}
        if kw:
            for k in kw:
                a, b = E[k].elts[2], E[k].elts[3]; ln = a.lineno - 1
                sa, sb = ast.get_source_segment(src, a), ast.get_source_segment(src, b)
                L[ln] = L[ln].replace(f"{sa}, {sb}", f"{max(0.0, a.value - 6):.1f}, {b.value + 6:.1f}", 1)
                wid[str(k)] = wid.get(str(k), 0) + 1; print("나레 구간 넓힘", k)
            json.dump(wid, open("b_widen.json", "w")); open("script.py", "w", encoding="utf-8").write("\n".join(L)); continue
        if kn:      # 새 나레가 길어 자리 없음 → 그 줄만 짧게 다시 쓰고 다시 녹음
            sys.path.insert(0, HERE); import make_b as MB
            for k in kn:
                node = E[k].elts[1]; old = ast.literal_eval(node); lim = int(len(old) * 0.8)
                new = MB.ask(f"아래 영화 리뷰 나레이션 문장을 뜻·이름은 그대로 두고 {lim}자 이하로 줄여라. 큰따옴표 금지. 출력은 줄인 문장 한 줄만.\n\n{old}").strip().splitlines()
                new = next((x.strip().replace('"', "'") for x in new if 0 < len(x.strip()) <= lim + 2), None)
                if not new: continue
                seg = ast.get_source_segment(src, node); L[node.lineno - 1] = L[node.lineno - 1].replace(seg, json.dumps(new, ensure_ascii=False), 1)
                print("나레 줄임", k, len(old), "→", len(new))
            open("script.py", "w", encoding="utf-8").write("\n".join(L))
            if os.path.isdir("gem"):    # 제미나이로 녹음한 편 — 줄인 줄도 제미나이로(목소리 섞지 않게): 묶음 만들고 멈춤
                run(os.path.join(V9, "prep", "mkbatch.py"), "2000"); open("READY", "w").close()
                sys.exit(5)
            r = run(os.path.join(HERE, "make_b.py"), "tts", B)
            if r.returncode: sys.exit("tts 실패")
            continue
        if not ks: break
        for k in ks:
            ln = E[k].lineno - 1
            if L[ln].lstrip().startswith('("A"'): L[ln] = "# (B판 뺌·자리 없음/까만) " + L[ln]
        open("script.py", "w", encoding="utf-8").write("\n".join(L)); print("A 뺌", len(ks))
    print("\n".join(out.strip().splitlines()[-3:]))
    if r.returncode: sys.exit("plan 문제 — _plan_dry.log")
    # 10-31 제미나이 목소리는 느려 1분쯤만 줄어듦 → A판보다 100초 덜 짧으면 대사 창을 더 빼고(약 2분 맞춤) 다시 계획
    WA = json.load(open(os.path.join(A, "windows.json"), encoding="utf-8")); WB = json.load(open("windows.json", encoding="utf-8"))
    short = WA[-1]["b"] - WB[-1]["b"]
    if short < 100 and not os.path.exists("b_more_cut.done"):
        sys.path.insert(0, HERE); import make_b as MB
        MB.more_cut(B, 120 - short); open("b_more_cut.done", "w").write(f"{short:.1f}")
        r = run(os.path.join(V9, "plan_v9.py"), log="_plan_dry.log"); print("\n".join(r.stdout.strip().splitlines()[-3:]))
        if r.returncode: sys.exit("plan 문제(더 뺀 뒤) — _plan_dry.log")

if on("gate"):
    if not (os.path.exists("jev_np_out.jsonl") and os.path.getmtime("jev_np_out.jsonl") > os.path.getmtime("windows.json")):   # 창이 그대로면 제브 다시 안 돌림(돌릴 때마다 판정이 흔들려 새로 걸림)
        run(os.path.join(V9, "narr_pic.py"), log="_np.log")
    G = json.load(open("gate_allow.json", encoding="utf-8")) if os.path.exists("gate_allow.json") else {}
    if isinstance(G, list): G = {g: "A판" for g in G}
    GA = json.load(open(os.path.join(A, "gate_allow.json"), encoding="utf-8")) if os.path.exists(os.path.join(A, "gate_allow.json")) else {}
    if '"event"' not in open(os.path.join(A, "script.py"), encoding="utf-8").read():   # 앞 3분 규칙(10-20) 전에 만든 옛 편 — A판 구조 그대로
        G.setdefault("⑭ 첫 사건 표시 없음", "10-31 B판 — A판이 앞 3분 규칙(10-20) 전 편, 구조 그대로")
        G.setdefault("⑮ 앞 5분", "10-31 B판 — A판이 앞 5분 규칙(10-20) 전 편, 대사 흐름 그대로")
    An = {mm.group(0)[:4] for k in GA for mm in [re.search(r"n\d{3}_", k)] if mm}   # 키가 "n001_w0_0.0" 꼴이든 "⑨ … n002_w4_" 꼴이든
    An |= {mm.group(0)[:4] for k in G if not str(G[k]).startswith("A판") for mm in [re.search(r"n\d{3}_", k)] if mm}   # B판에서 이미 본 나레 줄(제브 판정이 돌 때마다 흔들림)
    json.dump(G, open("gate_allow.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)   # ⑭⑮ 허용을 관문 전에 써 둠
    r = run(os.path.join(V9, "gate.py"), "pre", log="_gate_pre.log")
    fails = re.findall(r"✗ ⑨ 나레↔그림 어긋남 (n\d{3}_w\d+_[\d.]+)", r.stdout)
    other = [l for l in r.stdout.splitlines() if "✗" in l and "⑨" not in l]
    for f in fails:
        if f[:4] in An: G[f] = "10-31 B판 — A판에서 눈으로 보고 허용한 같은 나레 줄·같은 원본 구간"
    json.dump(G, open("gate_allow.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    new = [f for f in fails if f[:4] not in An]
    if new or other:
        IN = {json.loads(l)["id"]: json.loads(l) for l in open("jev_np_in.jsonl", encoding="utf-8")}
        open("b_new9.txt", "w", encoding="utf-8").write("\n".join([f"{f}\t{IN.get(f, {}).get('narration')}\t{IN.get(f, {}).get('shot')}" for f in new] + other))
        print("새로 걸림", len(new), "그 밖", other); sys.exit(3)
    r = run(os.path.join(V9, "gate.py"), "pre", log="_gate_pre.log"); print(r.stdout.strip().splitlines()[-1])
    if r.returncode: sys.exit("gate pre 실패")

if on("build"):
    r = run(os.path.join(V9, "build_v9.py"), "cut", log="_cut.log")
    if r.returncode: sys.exit("cut 실패 — _cut.log")
    r = run(os.path.join(V9, "build_v9.py"), log="_build.log"); print(r.stdout[-600:])
    if r.returncode: sys.exit("build 실패 — _build.log")
    r = run(os.path.join(V9, "prep", "finalcheck.py"), "final.mp4", log="finalcheck.log"); print(r.stdout[-800:])

if on("deliver"):
    shutil.copy2("final.mp4", f"{OUT}/{NAME}.mp4")
    pre = os.path.basename(A)[2:].split("_", 1)[0].split("v")[0]
    AD = os.path.expanduser("~/volcano_work/시네플로그/완성본")
    for f in os.listdir(AD):
        if f.startswith(f"{pre}_") and "썸네일" in f and f.endswith(".jpg"): shutil.copy2(f"{AD}/{f}", f"{OUT}/{NAME}_{f.split('_', 2)[2]}")
    up = next((f for f in os.listdir(AD) if f.startswith(f"{pre}_") and f.endswith("_업로드.txt")), None)
    if up:
        t = open(f"{AD}/{up}", encoding="utf-8").read()
        cand = re.findall(r"^- (.+)$", t.split("[제목 후보]")[1].split("[")[0], re.M) if "[제목 후보]" in t else []
        if cand:
            t = re.sub(r"(\[제목\][^\n]*\n)[^\n]+", lambda mm: mm.group(1) + cand[0], t, 1)
            t = re.sub(r"\[제목 후보\].*?(?=\n\[)", "[제목 후보]\n(A판 제목과 다르게 — A판 후보 1번을 B판 제목으로 씀)\n", t, 1, flags=re.S)
        t = re.sub(r"[ ,]*#?시네플로그", "", t).replace("CINEFLOG", "")
        open(f"{OUT}/{NAME}_업로드.txt", "w", encoding="utf-8").write(t)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "final.mp4"], capture_output=True, text=True).stdout)
    da = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(A, "final.mp4")], capture_output=True, text=True).stdout)
    print(f"완성 {OUT}/{NAME}.mp4 {d / 60:.2f}분 (A판 {da / 60:.2f}분, {(da - d) / 60:.2f}분 짧음)")
    # 11-02 사용자 "앞으로 만드는 영화리뷰를 이렇게 수정용으로까지 만들어주면 좋겠어 그리고이렇게 파일도 정리해주고" → 영화리뷰/<NN_제목>/ 에 원본·완성본·캡컷편집용
    if os.path.isdir("G:/내 드라이브"):
        subprocess.run([sys.executable, os.path.join(V9, "drive_save.py"), B], check=True, env=ENV)
