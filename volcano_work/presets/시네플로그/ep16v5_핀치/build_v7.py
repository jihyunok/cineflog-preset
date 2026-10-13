# -*- coding: utf-8 -*-
"""16 핀치 v7 (10-12 사용자 "이 만드니까 저작권에 걸려") — 벤치 장면 순서·나레 자리는 그대로, 원본 쓰는 법은 강의 규칙대로.
v6 문제: 벤치처럼 원본을 길게(평균 3.7초·최장 22초) 이어 쓰고 원본 소리도 길게 흘림 → CID.
v7:
- 벤치 시간축을 창(window)으로 다시 쪼갠다. 원본 창은 2.9초 이하(대사는 말 끝까지·5.9초 이하), 원본에서 앞뒤 3초 이상 떨어진 곳만(3/3).
  창의 원본 자리는 그 벤치 순간이 보여 주던 원본 자리(편집표) 가까이에서 찾는다 → 나레가 말하는 장면 그대로.
- 대사(우리 자막 있는 줄)는 나레가 없을 때만 통째로, 반전 없이. 나머지는 액션 창: 좌우반전 + 영상만 1.05배속.
- 창마다 원본 화면에서 박힌 글자를 재서(burn_detect 판정) 떠 있는 동안만 그 줄 위까지 확대. 색조 필터 전부. 자막·나레·소리·음원 15초는 v6 그대로.
사용: python build_v7.py plan → windows.json · cut → clips_v7/·body_v7.mkv · (없음) → final_v7.mp4"""
import json, math, os, re, subprocess, sys
import numpy as np
FF = ["ffmpeg", "-v", "error", "-y"]
SRC = "../ep16v4_핀치/src.mp4"; FPS = 24000 / 1001
W, H, BAR = 1920, 1080, 138
MAXC, GAP, SPD = 2.9, 3.0, 1.05
SP = json.load(open("bench_spans.json", encoding="utf-8")); SKIP = {119}
E = json.load(open("edl.json")); EVL = json.load(open("../ep16v4_핀치/subev.json"))
KO = json.load(open("../ep16v4_핀치/ko16.json", encoding="utf-8"))
DADD = {x["id"]: x["ko"] for x in json.load(open("dsubs.json", encoding="utf-8")) if x["ko"]}
DEND = json.load(open("../ep16v4_핀치/dend.json"))
PL = json.load(open("narr_place.json")); NAR = [(q["t"] - 0.25, q["t"] + q["d"] + 0.25) for q in PL]
cuts = np.array([float(x) for x in re.findall(r"pts_time:([\d.]+)", open("../ep16v4_핀치/scenes.txt").read())])
BODY = round(E[-1]["b1"], 3)
EQ = "eq=saturation=1.12:contrast=1.05:brightness=0.01,hue=h=4"
VF_BASE = "crop=1830:766:45:19,scale=1920:804," + EQ
MODE = sys.argv[1] if len(sys.argv) > 1 else "build"
def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
def src_at(t):
    g = next((g for g in E if g["b0"] <= t < g["b1"]), E[-1]); return g["s0"] + (t - g["b0"])
def under(a, b): return any(a < y and b > x for x, y in NAR)

if MODE == "plan":
    used = {"hook": [], "main": [], "crit": []}     # 훅·끝 비평은 예고편처럼 본편 장면을 다시 쓰는 자리 → 3/3 은 구역 안에서
    ZONE = ["main"]
    def zone(t): return "hook" if t < 85 else "crit" if t >= 1592 else "main"
    def free(s, e): return all(e + GAP <= a or s >= b + GAP for a, b in used[ZONE[0]]) and s >= 62
    def speech(s, e): return any(s < ev["e"] and e > ev["s"] for ev in EVL)
    # 1) 대사 창(나레 없을 때, 글 있는 줄) — 벤치에서 그 줄이 나오던 자리 그대로
    fixed = []
    for g in E:
        off = g["b0"] - g["s0"]
        for ev in EVL:
            if not (g["s0"] <= ev["s"] < g["s0"] + g["d"]): continue
            ko = KO.get(str(ev["id"])) or DADD.get(ev["id"])
            if not ko: continue
            s = ev["s"] - 0.05; e = min(ev["e"] + 0.25, DEND.get(str(ev["id"])) + 0.35 if DEND.get(str(ev["id"])) else 9e9)
            if e - s > 5.9: continue
            a, b = s + off, e + off
            if b > g["b1"] + 0.3 or under(a, b): continue
            ZONE[0] = zone(a)
            if not free(s, e): continue
            fixed.append({"a": round(a, 3), "b": round(b, 3), "s": round(s, 3), "kind": "D", "ko": ko}); used[ZONE[0]].append((s, e))
    fixed.sort(key=lambda w: w["a"])
    # 2) 사이를 액션 창으로 — 원하는 원본 자리 근처에서 3/3 지키는 곳 찾기
    def find(t, L):
        want = src_at(t); sl = L * SPD
        offs = sorted([k * 0.25 for k in range(-360, 361)], key=lambda o: (abs(o) if o >= 0 else abs(o) * 1.3))
        for o in offs:
            c = want + o
            near = cuts[(cuts >= c - 0.3) & (cuts <= c + 0.7)]       # 장면 전환 바로 뒤면 그쪽으로
            c2 = float(near[0]) + 0.08 if len(near) else c
            for cc in (c2, c):
                if free(cc, cc + sl) and not (not under(t, t + L) and speech(cc, cc + sl)):
                    return cc
        return None
    wins = []; t = 0.0; fi = 0; miss = 0
    while t < BODY - 0.05:
        nxt = fixed[fi]["a"] if fi < len(fixed) else BODY
        if t >= nxt - 0.05 and fi < len(fixed):
            w = fixed[fi]; w["a"] = round(t, 3); wins.append(w); t = w["b"]; fi += 1; continue
        ZONE[0] = zone(t); L = min(MAXC, nxt - t)
        if nxt - t - L < 0.8 and nxt - t > MAXC: L = (nxt - t) / 2       # 끝에 너무 짧은 꼬리가 남지 않게
        c = find(t, L)
        if c is None and L > 2.0: L = 2.0; c = find(t, L)
        if c is None: L = min(1.2, nxt - t); c = find(t, L)
        if c is None: miss += 1; c = src_at(t)
        used[ZONE[0]].append((c, c + L * SPD)); wins.append({"a": round(t, 3), "b": round(t + L, 3), "s": round(c, 3), "kind": "A"}); t += L
    json.dump(wins, open("windows.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    A = [w for w in wins if w["kind"] == "A"]; D = [w for w in wins if w["kind"] == "D"]
    close = 0
    for z in ("hook", "main", "crit"):
        sp = sorted([(w["s"], w["s"] + (w["b"] - w["a"]) * (SPD if w["kind"] == "A" else 1)) for w in wins if zone(w["a"]) == z])
        close += sum(1 for i in range(len(sp) - 1) if sp[i + 1][0] - sp[i][1] < GAP - 0.01)
    sp = sorted([(w["s"], w["s"] + (w["b"] - w["a"]) * (SPD if w["kind"] == "A" else 1)) for w in wins])
    drift = [abs(w["s"] - src_at(w["a"])) for w in A]
    print(f"창 {len(wins)} · 액션 {len(A)} · 대사 {len(D)}({sum(w['b']-w['a'] for w in D):.0f}초) · 최장 {max(w['b']-w['a'] for w in wins):.2f}초 · 3초 간격 어김 {close} · 자리 못 찾음 {miss}")
    print(f"원하던 원본 자리와 차이: 중앙 {np.median(drift):.1f}초 · 90% {np.percentile(drift, 90):.1f}초 · 원본 사용 {sum(b-a for a,b in sp)/60:.1f}분")
    sys.exit()

WN = json.load(open("windows.json", encoding="utf-8"))
os.makedirs("clips_v7", exist_ok=True)
Y0, HH, X0, WW = 560, 220, 360, 1200      # burn_detect.py 와 같은 판정
def score(a):
    w = a > 225; d = a < 50; nb = np.zeros_like(w)
    for dy, dx in ((1, 0), (2, 0), (0, 1), (0, 2), (-1, 0), (0, -1)): nb |= np.roll(np.roll(d, dy, 0), dx, 1)
    return int((w & nb).sum())
def top(a):
    r = np.where((a > 225).sum(1) > 4)[0]; return int(Y0 + r.min() * 2) if len(r) else 700
def frames(s0, L):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(s0, 0):.3f}", "-t", f"{L:.3f}", "-i", SRC,
                        "-vf", f"fps={FPS8},crop={WW}:{HH}:{X0}:{Y0},scale={WW//2}:{HH//2},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.uint8).reshape(-1, HH // 2, WW // 2)
FPS8 = 8
def burn(s0, L):
    a = frames(s0, L); sc = [score(x) for x in a]; out = []; i = 0
    while i < len(sc):
        if sc[i] > 60:
            j = i
            while j < len(sc) and sc[j] > 60: j += 1
            out.append((i / FPS8, j / FPS8, min(top(a[x]) for x in range(i, j)))); i = j
        else: i += 1
    return out
def cut(k):
    w = WN[k]; p = f"clips_v7/c{k:04d}.mkv"
    if os.path.exists(p): return p
    f0 = round(w["a"] * FPS); f1 = round(w["b"] * FPS); n = max(1, f1 - f0); L = n / FPS
    act = w["kind"] == "A"; sl = L * SPD if act else L
    bs = burn(w["s"], sl)
    ch = ["[0:v]" + ("setpts=PTS/1.05," if act else "") + "split=%d[b]" % (1 + len(bs)) + "".join(f"[z{i}]" for i in range(len(bs))), f"[b]{VF_BASE}[v0]"]
    for i, (a, b, tp) in enumerate(bs):
        h = max(540, min(700, tp - 12)); ww = round(1920 * h / 804 / 2) * 2
        a2, b2 = (a / SPD, b / SPD) if act else (a, b)
        ch.append(f"[z{i}]crop={ww}:{h}:{(1920 - ww) // 2}:0,scale=1920:804,{EQ}[zz{i}]")
        ch.append(f"[v{i}][zz{i}]overlay=0:0:enable='between(t,{max(0, a2 - 0.1):.3f},{b2 + 0.1:.3f})'[v{i + 1}]")
    ch.append(f"[v{len(bs)}]" + ("hflip," if act else "") + f"pad={W}:{H}:0:{BAR}:black,format=yuv420p[vo]")
    subprocess.run(FF + ["-ss", f"{max(w['s'], 0):.4f}", "-i", SRC, "-frames:v", str(n), "-filter_complex", ";".join(ch), "-map", "[vo]", "-map", "0:a:0",
                         "-af", f"apad,atrim=0:{L:.5f},afade=t=in:d=0.03,afade=t=out:st={max(0, L - 0.05):.3f}:d=0.05,aresample=48000",
                         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "pcm_s16le", "-ac", "2", "-r", "24000/1001", p], check=True)
    return p
if MODE == "cut":
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as ex: ps = list(ex.map(cut, range(len(WN))))
    open("all_v7.txt", "w").write("".join(f"file '{p}'\n" for p in ps))
    subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", "all_v7.txt", "-c", "copy", "body_v7.mkv"], check=True)
    print("창", len(ps), "· 몸통", round(dur("body_v7.mkv"), 2), "초 (벤치", BODY, ")"); sys.exit()

# ── 나레·소리·자막·굽기 (v6 와 같음)
BODY = dur("body_v7.mkv")
# 나레 놓기
narr = []
for i, x in enumerate(SP, 1):
    if i in SKIP: continue
    w = f"narr/n{i:03d}.wav"
    if not os.path.exists(w): sys.exit(f"나레 없음 {w}")
    d = dur(w); t = x["s"] + 0.05
    j = i + 1
    while j in SKIP: j += 1
    nxt = SP[j - 1]["s"] if j <= len(SP) else BODY + 20
    if t + d > nxt - 0.1: t = max(x["s"] - 0.3, nxt - 0.1 - d)          # 다음 자리를 넘으면 조금 당긴다
    narr.append((i, t, d, w))
over = [(narr[k][0], round(narr[k][1] + narr[k][2] - narr[k + 1][1], 2)) for k in range(len(narr) - 1) if narr[k][1] + narr[k][2] > narr[k + 1][1]]
print("나레", len(narr), "· 합", round(sum(d for _, _, d, _ in narr)), "초 · 비중", round(100 * sum(d for _, _, d, _ in narr) / BODY), "% · 겹침", over)
END = max(BODY, narr[-1][1] + narr[-1][2] + 1.5) + 15; OUT = END - BODY   # 강의: 아웃트로 뒤 음원 15초

# 원본 낮추기 구간(앞뒤 0.25초 여유) → volume 식
duck = []
for _, t, d, _ in narr:
    a, b = t - 0.25, t + d + 0.3
    if duck and a <= duck[-1][1]: duck[-1][1] = b
    else: duck.append([a, b])
# expr = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in duck)
# 원본 소리 크기: 몸통 전체를 -17 LUFS 로 맞추는 이득
o = subprocess.run(["ffmpeg", "-i", "body_v7.mkv", "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
import re
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]); g = max(-10, min(14, -17 - I))
print("원본", I, "LUFS → 이득", round(g, 1))

# 자막(ASS) — 나레만
from PIL import ImageFont
NS = 100; FN = ImageFont.truetype("../ep16v4_핀치/fonts/GyeonggiTitleB.ttf", NS); MAXW = 1300
def wid(t): return FN.getlength(t)
def balance(s):
    if wid(s) <= MAXW: return [s]
    ws = s.split(" "); k = math.ceil(wid(s) / MAXW)
    while True:
        tgt = len(s) / k; parts = [""]
        for w in ws:
            if parts[-1] and len(parts[-1]) + 1 + len(w) > tgt * 1.15 and len(parts) < k: parts.append(w)
            else: parts[-1] = (parts[-1] + " " + w).strip()
        if all(wid(p) <= MAXW for p in parts) or k > 6: break
        k += 1
    out = []
    for p in parts:
        if out and (len(p.replace(" ", "")) < 5 or len(out[-1].replace(" ", "")) < 5) and wid(out[-1] + " " + p) <= MAXW * 1.1: out[-1] += " " + p
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
                parts = balance(s); a0 = st[c0]; span = en[i] - a0; tot = sum(len(p) for p in parts)
                for p in parts:
                    d0 = span * len(p) / tot; out.append((p, a0, a0 + d0)); a0 += d0
            cur = ""; c0 = None
    return out
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"
ev = []
for i, t, d, w in narr:
    al = json.load(open(f"narr/n{i:03d}.json", encoding="utf-8")); cs = chunks("".join(al["chars"]), al["st"], al["en"])
    for k, (s, a, b) in enumerate(cs):
        a2 = t + a; b2 = t + (cs[k + 1][1] if k + 1 < len(cs) else b + 0.25)
        ev.append((a2, max(b2, a2 + 0.3), s))
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: N,GyeonggiTitle,{NS},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,-1,0,0,100,100,0,0,1,5,1,2,60,60,165,1
Style: D,Stylish,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,-1,0,0,100,100,0,0,1,5,1,2,60,60,165,1
Style: TOP,Noto Sans KR Black,104,&H00B5B5B5,&H00B5B5B5,&H00000000,&H64000000,-1,-1,0,0,100,100,0,0,1,4,0,9,40,40,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0)},{ts(END)},TOP,,0,0,0,,CINEFLOG
"""
for a, b, s in ev: ass += f"Dialogue: 0,{ts(a)},{ts(b)},N,,0,0,0,,{s}\n"
nd = 0
for w in WN:      # v7: 대사 창 = 우리 자막(나레 없을 때만 대사 창을 만들었다)
    if w["kind"] != "D": continue
    parts = w["ko"].split(" / "); n = len(parts)
    for k, part in enumerate(parts):
        a0 = w["a"] + 0.05 + (w["b"] - w["a"] - 0.1) * k / n; b0 = w["a"] + 0.05 + (w["b"] - w["a"] - 0.1) * (k + 1) / n
        ass += f"Dialogue: 0,{ts(a0)},{ts(max(b0, a0 + 0.6))},D,,0,0,0,,{part}\n"
    nd += 1
print("대사 자막", nd)
open("subs_v7.ass", "w", encoding="utf-8").write(ass)
json.dump([{"ni": i, "t": round(t, 3), "d": round(d, 3)} for i, t, d, _ in narr], open("narr_place.json", "w"), indent=0)

# 소리: numpy 로 원본(이득·나레 자리 낮춤, 0.15초 경사) + 나레를 섞어 mix_v7.wav, 원본만 낮춘 것은 org_v7.wav(캡컷용)
import numpy as np, wave
SR = 48000; N = int((END + 1) * SR)
def load(p):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.float32).reshape(-1, 2)
def save(p, x):
    with wave.open(p, "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
org = np.zeros((N, 2), np.float32); o0 = load("body_v7.mkv")[:N]; org[:len(o0)] = o0 * 10 ** (g / 20)
env = np.ones(N, np.float32); R = int(0.15 * SR)
for a, b in duck:
    ia, ib = max(0, int(a * SR)), min(N, int(b * SR)); env[ia:ib] = 0.2
    env[max(0, ia - R):ia] = np.minimum(env[max(0, ia - R):ia], np.linspace(1, 0.2, ia - max(0, ia - R)))
    env[ib:min(N, ib + R)] = np.minimum(env[ib:min(N, ib + R)], np.linspace(0.2, 1, min(N, ib + R) - ib))
org *= env[:, None]; save("org_v7.wav", org)
nar = np.zeros((N, 2), np.float32)
for i, t, d, w in narr:
    x = load(w); k = int(t * SR); nar[k:k + len(x)] += x[:N - k]
save("narr_track7.wav", nar); save("mix_v7.wav", org + nar)
t_mus = narr[-1][1] - 1.0
music = os.path.expanduser(r"~/volcano_work/달빛롱폼/bgm/") + "Healing.mp3"
inputs = ["-i", "body_v7.mkv", "-i", "mix_v7.wav", "-i", music]
fc = f"[2:a]aresample=48000,atrim=0:{END - t_mus + 1:.2f},volume=0.12,afade=t=in:d=2,afade=t=out:st={END - t_mus - 3:.2f}:d=3,adelay={int(t_mus*1000)}|{int(t_mus*1000)}[mus];" \
     f"[1:a][mus]amix=inputs=2:normalize=0:duration=first,atrim=0:{END:.2f},alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11[a];" \
     f"[0:v]unsharp=5:5:0.55:5:5:0,tpad=stop_mode=add:stop_duration={OUT:.2f}:color=black,subtitles=subs_v7.ass:fontsdir=../ep16v4_핀치/fonts[v]"
open("fc_v7.txt", "w", encoding="utf-8").write(fc)
subprocess.run(FF + inputs + ["-/filter_complex", "fc_v7.txt", "-map", "[v]", "-map", "[a]",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                              "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "final_v7.mp4"], check=True)
print("final_v7", round(dur("final_v7.mp4") / 60, 2), "분")
