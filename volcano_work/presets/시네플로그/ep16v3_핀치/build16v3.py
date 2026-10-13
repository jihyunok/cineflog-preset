# -*- coding: utf-8 -*-
"""시네플로그 16 핀치 다시 만들기 (2026-10-12) — 댓글 "편집 형편없고 무슨 얘긴지 모르겠다" 고친 빌더
옛 build16 과 다른 점(docs/영화리뷰_공부/벤치비교_지무비김시선_2026-10-12.md 「고칠 것」):
- 나레 화면 = 대본에 적은 그 장면 구간 [a,b] 안에서 시간 순서대로(넘치면 b 뒤로 최대 EXT 초까지만). 영화 전체에서 아무 데나 가져오지 않는다.
- 나레 컷은 좌우반전 안 함. 대사 컷만 3초 넘을 때 반전(공정사용 규칙 ≤3.95초).
- 대사는 말이 끝날 때까지(자막 끝 또는 dend.py 로 잰 말 끝 중 짧은 것). 3초 넘으면 좌우반전(변조 컷은 6초까지 — 강의 규칙), 5.9초 넘는 줄은 쓰지 않는다.
- 나레 자막: 문장·쉼표에서 끊고 폭이 넘치면 고르게 나누되 5자 미만 조각은 안 만든다.
- 3초 규칙(원본 컷 ≤2.9초, 쓴 구간끼리 3초 이상)은 그대로.
사용: python build16v3.py plan   → items.json + 검사(컷 모자람·대사 간격·긴 대사)
      python build16v3.py dry    → 나레 길이를 글자 수로 어림해 컷 고르기만 검사
      python build16v3.py prep   → 대사 컷만 자르기
      python build16v3.py        → 굽기 (narr/nNNN.wav·json 필요)
"""
import json, math, os, re, subprocess, sys, importlib
FF = ["ffmpeg", "-v", "error", "-y"]
SRC = "src.mp4"
SPEED = 1.05
MAXC = 2.9
GAP = 3.0
EXT = 25.0            # 장면 구간이 모자랄 때 뒤로 늘리는 한도
END = 6440.0
W, H, BAR = 1920, 1080, 138
EQ = "eq=saturation=1.12:contrast=1.04:brightness=0.01,hue=h=4"
VF_BASE = "crop=1830:766:45:19,scale=1920:804," + EQ
VF_ZOOM = "crop=1352:566:284:2,scale=1920:804," + EQ
SUBEV = [(e["s"] - 0.25, e["e"] + 0.25) for e in json.load(open("subev.json"))]
EV = {e["id"]: e for e in json.load(open("subev.json"))}
KO = json.load(open("ko16.json", encoding="utf-8"))
DEND = json.load(open("dend.json")) if os.path.exists("dend.json") else {}
BAN = [(0, 62)]       # 앞 로고 (제목을 넣기로 해서 이름 배지·팻말 금지는 뺐다)
CPS = 530 / 60        # 제미나이 Ludo 실측 약 530자/분
MODE = sys.argv[1] if len(sys.argv) > 1 else "build"
os.makedirs("clips", exist_ok=True); os.makedirs("blocks", exist_ok=True)

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)

# ── 계획: ep16v3.S → items.json
def plan_items():
    EP = importlib.import_module("ep16v3")
    items = []; ni = 0; warn = []
    for x in EP.S:
        if x[0] == "N":
            ni += 1; items.append({"type": "N", "ni": ni, "text": x[1], "rng": [x[2], x[3]]})
        elif x[0] == "A":
            items.append({"type": "D", "i": 0, "s": float(x[1]), "d": float(x[2]), "ko": "", "mirror": False})
        else:
            eid = x[1]; e = EV[eid]; ko = KO.get(str(eid), "X")
            if ko == "X": warn.append(f"대사 {eid} 글자 없음"); continue
            ln = round(e["e"] - e["s"] + 0.2, 2)
            if str(eid) in DEND and DEND[str(eid)]: ln = min(ln, round(DEND[str(eid)] - e["s"] + 0.35, 2))   # 실제 말 끝(dend.py)
            if 5.9 < ln <= 6.3: ln = 5.9             # 끝 0.4초 안 꼬리만 자름
            if ln > 5.9: warn.append(f"대사 {eid} {ln}초 너무 김 → 뺌 「{ko}」"); continue
            items.append({"type": "D", "i": eid, "s": round(e["s"] - 0.05, 3), "d": max(ln, 1.0), "ko": ko, "mirror": ln > 2.95})
    D = sorted((q for q in items if q["type"] == "D"), key=lambda q: q["s"])
    for a, b in zip(D, D[1:]):
        if b["s"] < a["s"] + a["d"] + GAP: warn.append(f"대사 간격 3초 미만: {a['i']}「{a['ko']}」 · {b['i']}「{b['ko']}」")
    return items, warn

if MODE == "plan":
    items, warn = plan_items()
    json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    nch = sum(len(q["text"]) for q in items if q["type"] == "N"); dd = [q for q in items if q["type"] == "D"]
    print(f"나레 {sum(q['type']=='N' for q in items)}조각 {nch}자 ≈ {nch/CPS/60:.1f}분 · 대사 {len(dd)}개 {sum(q['d'] for q in dd)/60:.1f}분 · 예상 {(nch/CPS+sum(q['d'] for q in dd))/60:.1f}분")
    for w in warn: print(" !", w)
    sys.exit()

IT = json.load(open("items.json", encoding="utf-8"))
cuts = [float(m) for m in re.findall(r"pts_time:([\d.]+)", open("scenes.txt").read())]
used = [(q["s"], q["s"] + q["d"]) for q in IT if q["type"] == "D"]

def free(s, e):
    return all(e + GAP <= a or s >= b + GAP for a, b in used) and all(e <= a or s >= b for a, b in BAN)

def pick(a, b, n, ls):
    """장면 구간 [a, b(+EXT)] 안에서 시간 순서대로 컷 n개. 장면 전환 직후를 먼저 본다. 못 채우면 (out, 모자람)."""
    out = []; x = a; hi = min(b + EXT, END)
    while len(out) < n:
        if out: x = max(x, out[-1][1] + GAP)
        cand = [c + 0.1 for c in cuts if x <= c + 0.1 <= x + 1.0]       # 1초 안에 장면 전환이 있으면 거기서 시작
        starts = cand + [x + k * 0.25 for k in range(int((hi - x) / 0.25) + 1)]
        got = None
        for s in starts:
            if s + ls > hi: break
            if free(s, s + ls): got = s; break
        if got is None: break
        out.append((got, got + ls)); used.append((got, got + ls)); x = got + ls
    return out, n - len(out), max([o[1] for o in out] + [b]) - b

def yellow(s, e): return any(s < y and e > x for x, y in SUBEV)
def clip(path, s, ls, speed, mirror, gain_db, lo):
    if os.path.exists(path): return
    vf = (VF_ZOOM if yellow(s, s + ls) else VF_BASE) + (",hflip" if mirror else "") + f",pad={W}:{H}:0:{BAR}:black,setpts=PTS/{speed},fps=30,format=yuv420p"
    af = (f"atempo={speed}," if speed != 1 else "") + f"volume={gain_db}dB" + (",alimiter=limit=0.9" if gain_db > 0 else "") + ",aresample=48000"
    subprocess.run(FF + ["-ss", f"{s:.3f}", "-t", f"{ls:.3f}", "-i", SRC, "-vf", vf, "-af", af, "-t", f"{lo:.3f}",
                         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "pcm_s16le", "-ac", "2", path], check=True)

segs = []; plan = []; short = []
def dclip(q):
    tag = f"d{int(q['s']*100):07d}"; p = f"blocks/{tag}.mkv"
    if MODE != "dry": clip(p, q["s"], q["d"], 1, q["mirror"], 17.5 if q["ko"] else 6, q["d"])
    plan.append({"blk": tag, "type": "D", "src": [q["s"], round(q["s"] + q["d"], 2)], "mirror": q["mirror"]})
    segs.append(("D", p, {"ko": q["ko"]}))

def nseg(q):
    tag = f"n{q['ni']:03d}"; nw = f"narr/{tag}.wav"; nj = f"narr/{tag}.json"
    nd = len(q["text"]) / CPS + 0.4 if MODE == "dry" else dur(nw)
    total = nd + 0.12; n = max(1, math.ceil(total / (MAXC / SPEED))); lo = total / n; ls = lo * SPEED
    a, b = q["rng"]; picks, miss, over = pick(a, b, n, ls)
    if miss or over > 0.5: short.append((q["ni"], q["text"][:22], a, b, n, miss, round(over, 1)))
    if MODE == "dry":
        for s0, e0 in picks: plan.append({"blk": tag, "type": "N", "src": [round(s0, 2), round(e0, 2)]})
        return
    if miss: sys.exit(f"컷 모자람 n{q['ni']:03d} {a}-{b} (dry 로 먼저 고칠 것)")
    cl = []
    for k, (s0, e0) in enumerate(picks):
        p = f"clips/{tag}_{k}.mkv"; clip(p, s0, ls, SPEED, False, -13, lo); cl.append(p)
        plan.append({"blk": tag, "type": "N", "src": [round(s0, 2), round(e0, 2)]})
    out = f"blocks/{tag}.mkv"
    if not os.path.exists(out):
        lst = f"blocks/{tag}.txt"; open(lst, "w").write("".join(f"file '../{c}'\n" for c in cl))
        subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", lst, "-i", nw, "-filter_complex",
                             "[1:a]adelay=60|60,apad[n];[0:a][n]amix=inputs=2:normalize=0:duration=first[a]",
                             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "pcm_s16le", out], check=True)
    segs.append(("N", out, {"json": nj}))

if MODE == "prep":
    for q in IT:
        if q["type"] == "D": dclip(q)
    print("대사 컷", sum(q["type"] == "D" for q in IT)); sys.exit()

for q in IT:
    (nseg if q["type"] == "N" else dclip)(q)
json.dump(plan, open("cut_plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
srcs = sorted(p["src"] for p in plan)
close = [(srcs[i], srcs[i + 1]) for i in range(len(srcs) - 1) if srcs[i + 1][0] - srcs[i][1] < GAP - 0.01]
print(f"컷 {len(plan)} · 3초 넘는 컷 {sum(1 for a,b in srcs if b-a>2.95)}(대사 반전) · 간격 3초 미만 {len(close)} · 장면 넘침 {len(short)}")
for s in short: print(" ! n%03d 「%s」 %d-%d 컷%d 모자람%d 넘침%.1f초" % s)
if MODE == "dry": sys.exit()

# ── 자막(ASS)
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"
from PIL import ImageFont
FN = ImageFont.truetype("fonts/GyeonggiTitleB.ttf", 84); FD = ImageFont.truetype("fonts/Stylish.ttf", 88)
MAXW = 1100
def wid(t, f): return f.getlength(t)
def balance(s, f):
    """폭이 넘치면 낱말 경계에서 k 덩어리로 고르게 — 5자 미만 덩어리는 이웃에 붙인다."""
    if wid(s, f) <= MAXW: return [s]
    ws = s.split(" "); k = math.ceil(wid(s, f) / MAXW)
    while True:
        tgt = len(s) / k; parts = [""]
        for w in ws:
            if parts[-1] and len(parts[-1]) + 1 + len(w) > tgt * 1.15 and len(parts) < k: parts.append(w)
            else: parts[-1] = (parts[-1] + " " + w).strip()
        if all(wid(p, f) <= MAXW for p in parts) or k > 6: break
        k += 1
    out = []
    for p in parts:
        if out and (len(p.replace(" ", "")) < 5 or len(out[-1].replace(" ", "")) < 5) and wid(out[-1] + " " + p, f) <= MAXW * 1.1: out[-1] += " " + p
        else: out.append(p)
    return out
def chunks(text, st, en):
    out = []; cur = ""; c0 = None
    for i, ch in enumerate(text):
        if c0 is None:
            if ch == " ": continue
            c0 = i
        cur += ch
        if ch in ".?!" or (ch == "," and len(cur.strip()) >= 8) or i == len(text) - 1:
            s = cur.strip().rstrip(".,")
            if s:
                parts = balance(s, FN); a0 = st[c0]; span = en[i] - a0; tot = sum(len(p) for p in parts)
                for p in parts:
                    d0 = span * len(p) / tot; out.append((p, a0, a0 + d0)); a0 += d0
            cur = ""; c0 = None
    return out
ev = []; t0 = 0.0
for kind, p, m in segs:
    L = dur(p)
    if kind == "N":
        al = json.load(open(m["json"], encoding="utf-8"))
        cs = chunks("".join(al["chars"]), al["st"], al["en"])
        for k, (s, a, b) in enumerate(cs):
            a2 = t0 + 0.06 + a; b2 = t0 + 0.06 + (cs[k + 1][1] if k + 1 < len(cs) else b + 0.25)
            ev.append(("N", a2, min(b2, t0 + L), s))
    elif m["ko"]:
        ps = balance(m["ko"], FD); a0 = t0 + 0.05; span = L - 0.07; tot = sum(len(x) for x in ps)
        for x in ps:
            d0 = span * len(x) / tot; ev.append(("D", a0, a0 + d0, x)); a0 += d0
    t0 += L
BODY = t0
ev = [(k, a, max(b, a + 0.3), s) for k, a, b, s in ev]      # 끝<=시작 줄이 있으면 libass 가 로고까지 안 그린다(15·17편)
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: N,GyeonggiTitle,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,-1,0,0,100,100,0,0,1,4,1,2,60,60,100,1
Style: D,Stylish,88,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,-1,0,0,100,100,0,0,1,4,1,2,60,60,100,1
Style: TOP,Noto Sans KR Black,104,&H00B5B5B5,&H00B5B5B5,&H00000000,&H64000000,-1,-1,0,0,100,100,0,0,1,4,0,9,40,40,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0)},{ts(BODY)},TOP,,0,0,0,,CINEFLOG
"""
for k, a, b, s in ev:
    ass += f"Dialogue: 0,{ts(a)},{ts(b)},{k},,0,0,0,,{s}\n"
open("subs.ass", "w", encoding="utf-8").write(ass)

lst = "all.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for _, p, _ in segs))
subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "body.mkv"], check=True)
nlast = [i for i, s in enumerate(segs) if s[0] == "N"][-4]
t_out = sum(dur(p) for _, p, _ in segs[:nlast])
OUT = 18
music = os.path.expanduser(r"~/volcano_work/달빛롱폼/bgm/") + "Healing.mp3"
mus = f"music_{os.getpid()}.mp3"; subprocess.run(FF + ["-i", music, "-t", str(BODY - t_out + OUT), "-c", "copy", mus], check=True)
fc = (f"[0:v]pad=iw:ih,tpad=stop_mode=add:stop_duration={OUT}:color=black,subtitles=subs.ass:fontsdir=fonts[v];"
      f"[0:a]apad=pad_dur={OUT}[b];"
      f"[1:a]aresample=48000,volume='if(lt(t,{BODY - t_out:.2f}),0.10,0.5)':eval=frame,afade=t=in:d=2,afade=t=out:st={BODY - t_out + OUT - 3:.2f}:d=3,adelay={int(t_out*1000)}|{int(t_out*1000)}[m];"
      f"[b][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
subprocess.run(FF + ["-i", "body.mkv", "-i", mus, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "final.mp4"], check=True)
print("final", round(dur("final.mp4") / 60, 2), "분")
