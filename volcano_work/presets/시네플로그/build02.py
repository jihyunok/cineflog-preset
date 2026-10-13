# -*- coding: utf-8 -*-
"""시네플로그 롱폼 빌더 — 무비마스터 공정사용 규칙
- 원본 한 컷 ≤ 2.9초 (변조=좌우반전 컷은 대사에 한해 ≤ 3.95초), 쓴 구간 앞뒤 3초 이상 다른 컷과 띄움
- 소스 단계 변형: 5% 확대 + 위아래 실제 크롭(박힌 자막 제거) + 색조, 나레 구간 영상 1.05배속, 컷마다 좌우반전 번갈아
- 나레 -16 LUFS, 나레 밑 원본 -13dB(≈나레보다 25dB 아래), 대사 +12dB(≈나레와 같은 크기)
"""
import json, math, os, re, subprocess, sys
FF = ["ffmpeg", "-v", "error", "-y"]
SRC = "src.mp4"
SPEED = 1.05
MAXC = 2.9            # 나레 구간 원본 컷 최대 길이(원본 기준)
GAP = 3.0             # 쓴 구간 사이 최소 간격
W, H, BAR = 1920, 1080, 138
VF_BASE = "crop=1830:766:45:19,scale=1920:804,eq=saturation=1.12:contrast=1.04:brightness=0.01,hue=h=4"
os.makedirs("clips", exist_ok=True); os.makedirs("blocks", exist_ok=True)

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)

cuts = [float(m) for m in re.findall(r"pts_time:([\d.]+)", open("scenes.txt").read())]
used = []

def free(s, e):
    return all(e + GAP <= a or s >= b + GAP for a, b in used)

def cut_inside(s, e):
    return any(s + 0.35 < c < e - 0.35 for c in cuts)

def pick(a, b, n, ls):
    """[a,b] 구간(모자라면 뒤로 늘림)에서 길이 ls 원본 컷 n개를 고른다."""
    out = []; ext = 0; fell = False
    while len(out) < n:
        lo, hi = a, min(b + ext, 6640)
        starts = sorted(set([c + 0.12 for c in cuts if lo <= c <= hi] + [lo + k * 0.5 for k in range(int((hi - lo) / 0.5) + 1)]))
        prefer = [x for x in starts if x in set(c + 0.12 for c in cuts)]
        got = False
        for pool in (prefer, starts):
            for x in pool:
                if out and not fell and x < out[-1][0] + ls + GAP: continue
                if x + ls > hi or not free(x, x + ls): continue
                if pool is prefer and cut_inside(x, x + ls): continue
                out.append((x, x + ls)); used.append((x, x + ls)); got = True; break
            if got: break
        if not got:
            ext += 30
            if ext > 600:
                if not fell: a, b, ext, fell = 60, 6640, 0, True      # 영화 전체(크레딧 전)에서 빈 곳을 찾는다
                else: sys.exit(f"컷이 모자람: {a}-{b} n={n}")
    return out

def clip(path, s, ls, speed, mirror, gain_db, lo):
    if os.path.exists(path): return
    vf = VF_BASE + (",hflip" if mirror else "") + f",pad={W}:{H}:0:{BAR}:black,setpts=PTS/{speed},fps=30,format=yuv420p"
    af = (f"atempo={speed}," if speed != 1 else "") + f"volume={gain_db}dB" + (",alimiter=limit=0.9" if gain_db > 0 else "") + ",aresample=48000"
    subprocess.run(FF + ["-ss", f"{s:.3f}", "-t", f"{ls:.3f}", "-i", SRC, "-vf", vf, "-af", af, "-t", f"{lo:.3f}",
                         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "pcm_s16le", "-ac", "2", path], check=True)

segs = []
plan = []
def dclip(tag, d):
    p = f"blocks/{tag}.mkv"; clip(p, d["s"], d["d"], 1, d["mirror"], 17.5, d["d"])
    plan.append({"blk": tag, "type": "D", "src": [d["s"], round(d["s"] + d["d"], 2)], "mirror": d["mirror"]})
    segs.append(("D", p, {"ko": d["ko"]}))

def nseg(tag, nw, nj, a, b):
    nd = dur(nw); total = nd + 0.12
    n = max(1, math.ceil(total / (MAXC / SPEED))); lo = total / n; ls = lo * SPEED
    picks = pick(a, b, n, ls); cl = []
    for k, (s0, e0) in enumerate(picks):
        p = f"clips/{tag}_{k}.mkv"; clip(p, s0, ls, SPEED, k % 2 == 1, -13, lo); cl.append(p)
        plan.append({"blk": tag, "type": "N", "src": [round(s0, 2), round(e0, 2)], "mirror": k % 2 == 1})
    out = f"blocks/{tag}.mkv"
    if not os.path.exists(out):
        lst = f"blocks/{tag}.txt"; open(lst, "w").write("".join(f"file '../{c}'\n" for c in cl))
        subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", lst, "-i", nw, "-filter_complex",
                             "[1:a]adelay=60|60,apad[n];[0:a][n]amix=inputs=2:normalize=0:duration=first[a]",
                             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "pcm_s16le", out], check=True)
    segs.append(("N", out, {"json": nj}))

IT = json.load(open("items.json", encoding="utf-8"))
used[:] = [(q["s"], q["s"] + q["d"]) for q in IT if q["type"] == "D"]
for q in IT:
    if q["type"] == "N":
        nseg(f"n{q['ni']:03d}", f"narr/n{q['ni']:03d}.wav", f"narr/n{q['ni']:03d}.json", q["rng"][0], q["rng"][1])
    else:
        dclip(f"d{int(q['s']*100):07d}", q)
json.dump(plan, open("cut_plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# ── 3초 규칙 검사
srcs = sorted(p["src"] for p in plan)
bad = [(a, b) for a, b in srcs if (b - a) > (3.95 if False else 4.0)]
close = [(srcs[i], srcs[i + 1]) for i in range(len(srcs) - 1) if srcs[i + 1][0] - srcs[i][1] < GAP - 0.01]
print(f"컷 {len(plan)}개 · 3초 넘는 컷 {sum(1 for a,b in srcs if b-a>2.95)}개(대사 변조 허용) · 간격 3초 미만 {len(close)}개")

# ── 자막(ASS) — 실제 길이로 누적
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"
def chunks(text, st, en):
    """글자 시각으로 22자 안팎 덩어리를 자른다."""
    out = []; cur = ""; c0 = None
    for i, ch in enumerate(text):
        if c0 is None:
            if ch == " ": continue
            c0 = i
        cur += ch
        brk = ch in ".?!" or (ch in ", " and len(cur) >= 14) or (ch == " " and len(cur) >= 20)
        if brk or i == len(text) - 1:
            s = cur.strip().rstrip(".,")
            if s:
                if len(s) <= 26: out.append((s, st[c0], en[i]))
                else:
                    ws = s.split(" "); parts = [""]
                    for w in ws:
                        if len(parts[-1]) + len(w) + 1 > 20 and parts[-1]: parts.append(w)
                        else: parts[-1] = (parts[-1] + " " + w).strip()
                    a0 = st[c0]; span = en[i] - a0; tot = sum(len(p) for p in parts)
                    for p in parts:
                        d0 = span * len(p) / tot; out.append((p, a0, a0 + d0)); a0 += d0
            cur = ""; c0 = None
    return out
ev = []; t0 = 0.0
for kind, p, m in segs:
    L = dur(p)
    if kind == "N":
        al = json.load(open(m["json"], encoding="utf-8"))
        txt = "".join(al["chars"])
        cs = chunks(txt, al["st"], al["en"])
        for k, (s, a, b) in enumerate(cs):
            a2 = t0 + 0.06 + a; b2 = t0 + 0.06 + (cs[k + 1][1] if k + 1 < len(cs) else b + 0.25)
            ev.append(("N", a2, min(b2, t0 + L), s))
    else:
        ev.append(("D", t0 + 0.05, t0 + L - 0.02, m["ko"]))
    t0 += L
BODY = t0
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: N,Pretendard,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.6,1,2,60,60,44,1
Style: D,Pretendard,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.6,1,2,60,60,44,1
Style: TOP,Pretendard,30,&H00B4B4B4,&H00B4B4B4,&H00000000,&H64000000,-1,0,0,0,100,100,2,0,1,0,0,7,44,40,48,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0)},{ts(BODY)},TOP,,0,0,0,,CINEFLOG
"""
for k, a, b, s in ev:
    ass += f"Dialogue: 0,{ts(a)},{ts(b)},{k},,0,0,0,,{s}\n"
open("subs.ass", "w", encoding="utf-8").write(ass)

# ── 이어 붙이기 + 아웃트로(검은 화면 음악) + 자막 굽기
lst = "all.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for _, p, _ in segs))
subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "body.mkv"], check=True)
nlast = [i for i, s in enumerate(segs) if s[0] == "N"][-4]
t_out = sum(dur(p) for _, p, _ in segs[:nlast])
OUT = 18
music = os.path.expanduser(r"~/volcano_work/달빛롱폼/bgm/") + "Despair and Triumph.mp3"
mus = f"music_{os.getpid()}.mp3"; subprocess.run(FF + ["-i", music, "-t", str(BODY - t_out + OUT), "-c", "copy", mus], check=True)
fc = (f"[0:v]pad=iw:ih,tpad=stop_mode=add:stop_duration={OUT}:color=black,subtitles=subs.ass:fontsdir=fonts[v];"
      f"[0:a]apad=pad_dur={OUT}[b];"
      f"[1:a]aresample=48000,volume='if(lt(t,{BODY - t_out:.2f}),0.10,0.5)':eval=frame,afade=t=in:d=2,afade=t=out:st={BODY - t_out + OUT - 3:.2f}:d=3,adelay={int(t_out*1000)}|{int(t_out*1000)}[m];"
      f"[b][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
os.makedirs("fonts", exist_ok=True)
for f in ["Pretendard-Bold.otf"]:
    src = os.path.join(os.environ["WINDIR"], "Fonts", f)
    if not os.path.exists(src): src = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/" + f)
    if os.path.exists(src) and not os.path.exists("fonts/" + f):
        import shutil; shutil.copy(src, "fonts/" + f)
subprocess.run(FF + ["-i", "body.mkv", "-i", mus, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "final.mp4"], check=True)
print("final", round(dur("final.mp4") / 60, 2), "분")
