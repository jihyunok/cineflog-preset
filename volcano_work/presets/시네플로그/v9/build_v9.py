# -*- coding: utf-8 -*-
"""시네플로그 v9 굽기 — plan_v9.py 가 짠 windows.json · narr_place.json 그대로. 굽기 전에 gate.py 를 꼭 통과해야 한다.
★10-14 (17 그레이하운드 Apple IPE 영상 소유권 주장 뒤 "그렇게해줘"): 모든 조각 좌우반전(noflip 빼고) · 확대 1.12배(noflip 은 1.2배) · 색조·선명도 한 단계 세게 ·
  액션 조각 = 영상만 1.05배속 · 대사 창 = drate.py 가 적은 rate(≤1.05)·pre 로 영상·소리 같이 배속(입 모양 맞음, 낱말 안 잘림) · 박힌 자막이 떠 있는 동안만 그 줄 위까지 확대 ·
  (옛 v9: 대사 창은 반전·배속 없이 1.0배·확대 1.05배 → 대사 창이 63% 인 17편이 걸림)
★10-14 v11: v10 도 소유권 주장 그대로 → 대사 창은 화면 3초 안(plan_v9 가 처음부터 rate 1.05·pre 0 으로 짬, drate.py 안 씀) · 넘는 대사는 나레로. gate ⑫ 가 3초 넘는 조각을 막는다.
색조 eq 전부 · 자막(나레 경기천년제목 100 · 대사 나다스탈리크 104, 그림 안 아래 MarginV 165) · 원본 -17 LUFS 이득, 나레 밑 0.2 · 끝 음원은 아웃트로 밑에만(10-14 끝 검은 화면 뺌) · 최종 -16 LUFS.
사용: python build_v9.py cut    (gate pre 통과 뒤 조각 자르기 → body.mkv)
      python build_v9.py        (자막·소리 → gate final → final.mp4)
      python build_v9.py subs   (자막만 다시)"""
import json, math, os, re, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
FF = ["ffmpeg", "-v", "error", "-y"]
CFG = json.load(open("ep.json", encoding="utf-8"))
SRC = CFG["src"]; FPS = CFG.get("fps", 24000 / 1001); SH = CFG.get("h", 804)       # 원본 그림 높이
W, H = 1920, 1080; BAR = (H - SH) // 2; SPD = 1.05
EQ = "eq=saturation=1.25:contrast=1.08:brightness=0.015:gamma=1.02,hue=h=6"          # 10-14 한 단계 세게(옛 1.12·1.05·0.01·4)
ZOOM, ZOOM_NF, SHARP = 1.12, 1.2, 0.85                                                # 10-14 확대 1.05→1.12(반전 못 하는 글자 컷 1.2) · 선명도 0.55→0.85
def vf_base(z):
    cw = round(1920 / z / 2) * 2; chh = round(SH / z / 2) * 2
    return f"crop={cw}:{chh}:{(1920 - cw) // 2}:{(SH - chh) // 2},scale=1920:{SH}," + EQ
CLIPS = CFG.get("clips", "clips")
MODE = sys.argv[1] if len(sys.argv) > 1 else "build"
FONTS = CFG.get("fonts", "fonts")
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
def gate(*a):
    r = subprocess.run([sys.executable, os.path.join(HERE, "gate.py"), *a], text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0: sys.exit("관문에 걸림 — 굽지 않는다(위 목록을 고친 뒤 다시)")

WN = json.load(open("windows.json", encoding="utf-8"))
os.makedirs(CLIPS, exist_ok=True)
Y0, HH, X0, WWD = 560, 220, 360, 1200          # 박힌 자막 자리(burn_detect 와 같은 판정)
def score(a):
    w = a > 225; d = a < 50; nb = np.zeros_like(w)
    for dy, dx in ((1, 0), (2, 0), (0, 1), (0, 2), (-1, 0), (0, -1)): nb |= np.roll(np.roll(d, dy, 0), dx, 1)
    return int((w & nb).sum())
def top(a):
    r = np.where((a > 225).sum(1) > 4)[0]; return int(Y0 + r.min() * 2) if len(r) else 700
FPS8 = 8
def frames(s0, L):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(s0, 0):.3f}", "-t", f"{L:.3f}", "-i", SRC,
                        "-vf", f"fps={FPS8},crop={WWD}:{HH}:{X0}:{Y0},scale={WWD//2}:{HH//2},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.uint8).reshape(-1, HH // 2, WWD // 2)
def burn(s0, L):
    a = frames(s0, L); sc = [score(x) for x in a]; out = []; i = 0
    while i < len(sc):
        if sc[i] > 60:
            j = i
            while j < len(sc) and sc[j] > 60: j += 1
            out.append((i / FPS8, j / FPS8, min(top(a[x]) for x in range(i, j)))); i = j
        else: i += 1
    return out
def key(w): return f"{w['kind']}_{w['s']:.3f}_{w['b'] - w['a']:.3f}_{int(bool(w.get('noflip')))}_{w.get('rate', 0):.4f}_{w.get('pre', 0):.3f}"
def cut(k):
    w = WN[k]; p = f"{CLIPS}/{key(w)}.mkv"
    if os.path.exists(p): return p
    f0 = round(w["a"] * FPS); f1 = round(w["b"] * FPS); n = max(1, f1 - f0); L = n / FPS
    act = w["kind"] == "A"; r = w.get("rate", SPD if act else 1.0); sl = L * r; s0 = w["s"] - w.get("pre", 0)
    flip = not w.get("noflip")
    bs = burn(s0, sl)
    ch = ["[0:v]" + (f"setpts=PTS/{r:.4f}," if r != 1 else "") + "split=%d[b]" % (1 + len(bs)) + "".join(f"[z{i}]" for i in range(len(bs))), f"[b]{vf_base(ZOOM if flip else ZOOM_NF)}[v0]"]
    for i, (a, b, tp) in enumerate(bs):
        h = max(540, min(SH - 104, tp - 12)); ww = round(1920 * h / SH / 2) * 2
        a2, b2 = a / r, b / r
        ch.append(f"[z{i}]crop={ww}:{h}:{(1920 - ww) // 2}:0,scale=1920:{SH},{EQ}[zz{i}]")
        ch.append(f"[v{i}][zz{i}]overlay=0:0:enable='between(t,{max(0, a2 - 0.1):.3f},{b2 + 0.1:.3f})'[v{i + 1}]")
    ch.append(f"[v{len(bs)}]" + ("hflip," if flip else "") + f"pad={W}:{H}:0:{BAR}:black,format=yuv420p[vo]")
    subprocess.run(FF + ["-ss", f"{max(s0, 0):.4f}", "-i", SRC, "-frames:v", str(n), "-filter_complex", ";".join(ch), "-map", "[vo]", "-map", "0:a:0",
                         "-af", (f"atempo={r:.4f}," if not act and r != 1 else "") + f"apad,atrim=0:{L:.5f},afade=t=in:d=0.03,afade=t=out:st={max(0, L - 0.05):.3f}:d=0.05,aresample=48000",
                         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "pcm_s16le", "-ac", "2", "-r", "24000/1001", p + ".tmp.mkv"], check=True)
    os.replace(p + ".tmp.mkv", p)
    return p
if MODE == "cut":
    gate("pre")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as ex: ps = list(ex.map(cut, range(len(WN))))
    open("all.txt", "w", encoding="utf-8").write("".join(f"file '{p}'\n" for p in ps))
    subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", "all.txt", "-c", "copy", "body.mkv"], check=True)
    print("조각", len(ps), "· 몸통", round(dur("body.mkv"), 2), "초 (계획", round(WN[-1]["b"], 2), ")"); sys.exit()

# ── 나레·자막·소리·굽기
BODY = dur("body.mkv")
PL = json.load(open("narr_place.json"))
narr = [(q["ni"], q["t"], dur(f"narr/n{q['ni']:03d}.wav"), f"narr/n{q['ni']:03d}.wav") for q in PL]
NS = sum(d for _, _, d, _ in narr)
print("나레", len(narr), "· 합", round(NS), "초 · 비중", round(100 * NS / BODY), "%")
END = max(BODY, narr[-1][1] + narr[-1][2] + 1.5); OUT = END - BODY      # ★10-14 사용자 "영상 끝나고 10초넘게 시커먼화면이 나오는거확인하고 지워" → 옛 「아웃트로 뒤 음원 15초」(검은 화면) 뺌, 마지막 나레 1.5초 뒤 끝
NAR = [(t - 0.25, t + d + 0.25) for _, t, d, _ in narr]
def under(a, b): return any(a < y and b > x for x, y in NAR)

from PIL import ImageFont
NSZ = 100; FN = ImageFont.truetype(f"{FONTS}/GyeonggiTitleB.ttf", NSZ); MAXW = 1300
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
    """문장(. ? ! , 8자+)마다 자막 덩어리, 길면 balance 로 나누고 줄마다 그 줄 첫 글자의 실제 시각"""
    out = []; cur = ""; c0 = None
    for i, ch in enumerate(text):
        if c0 is None:
            if ch == " ": continue
            c0 = i
        cur += ch
        if ch in ".?!" or (ch == "," and len(cur.strip()) >= 8) or i == len(text) - 1:
            s = cur.strip().rstrip(".,")
            if s:
                parts = balance(s); pos = c0; starts = []
                for p in parts:
                    pos = text.find(p, pos); starts.append(pos); pos += len(p)
                for k, p in enumerate(parts):
                    a0 = st[starts[k]]; b0 = st[starts[k + 1]] if k + 1 < len(parts) else en[i]
                    if out and a0 < out[-1][1] + 0.3: a0 = out[-1][1] + 0.3
                    out.append((p, a0, max(b0, a0 + 0.3)))
            cur = ""; c0 = None
    return out
def voice_on(w):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", w, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, np.float32); on = np.sqrt(np.mean(x[:len(x) // 160 * 160].reshape(-1, 160) ** 2, 1)) > 0.02; k = 0
    while k < len(on):
        if not on[k]:
            j = k
            while j < len(on) and not on[j]: j += 1
            if j - k < 15 and k > 0: on[k:j] = True
            k = j
        else: k += 1
    return on
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"
def tsec(x):
    h, m, s = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
ev = []; snapped = 0
for i, t, d, w in narr:
    al = json.load(open(f"narr/n{i:03d}.json", encoding="utf-8")); cs = chunks("".join(al["chars"]), al["st"], al["en"])
    on = voice_on(w)
    for k in range(len(cs)):          # 줄 시작이 무음이면 실제 목소리 시작으로(subcheck4 잣대)
        s, a, b = cs[k]; f = min(max(int(a * 100), 0), len(on) - 1)
        if not on[f]:
            j = f
            while j < len(on) and not on[j]: j += 1
            nxt = cs[k + 1][1] if k + 1 < len(cs) else b + 0.25
            if 0.15 < j / 100 - a and j / 100 < nxt - 0.3: cs[k] = (s, j / 100, max(b, j / 100 + 0.3)); snapped += 1
    for k, (s, a, b) in enumerate(cs):
        a2 = t + a; b2 = t + (cs[k + 1][1] if k + 1 < len(cs) else min(b + 0.25, d))
        ev.append((a2, max(b2, a2 + 0.3), s))
print("목소리 시작에 맞춘 나레 자막 줄", snapped)
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: N,GyeonggiTitle,{NSZ},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,-1,0,0,100,100,0,0,1,5,1,2,60,60,165,1
Style: D,Stylish,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,-1,0,0,100,100,0,0,1,5,1,2,60,60,165,1
Style: TOP,Noto Sans KR Black,104,&H00B5B5B5,&H00B5B5B5,&H00000000,&H64000000,-1,-1,0,0,100,100,0,0,1,4,0,9,40,40,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
rows = [f"Dialogue: 0,{ts(a)},{ts(b)},N,,0,0,0,,{s}" for a, b, s in ev]
nd = 0
for w in WN:
    if w["kind"] != "D": continue
    pre, rr = w.get("pre", 0), w.get("rate", 1.0)          # drate: 원본 시각 → 화면 시각 (원본 t → (t + pre) / rate)
    if "subs" in w: parts = [(p, w["a"] + (a + pre) / rr, w["a"] + (b + pre) / rr) for p, a, b in w["subs"]]
    else:
        ps = w["ko"].split(" / "); n = len(ps); s0, e1 = 0.05, w.get("sub1", w["b"] - w["a"] - 0.05)
        tot = sum(len(p) for p in ps); acc = 0; parts = []
        for p in ps:
            a0 = w["a"] + (s0 + (e1 - s0) * acc / tot + pre) / rr; acc += len(p); parts.append((p, a0, w["a"] + (s0 + (e1 - s0) * acc / tot + pre) / rr))
    for p, a0, b0 in parts: rows.append(f"Dialogue: 0,{ts(a0)},{ts(max(b0, a0 + 0.6))},D,,0,0,0,,{p}")
    nd += 1
print("대사 창 자막", nd)
rows.sort(key=lambda r: tsec(r.split(",")[1])); cutn = 0
for k in range(len(rows) - 1):           # 두 줄 겹침 없게: 앞 줄은 다음 줄 뜨기 0.02초 전에 끈다
    f = rows[k].split(",", 9); nxt = tsec(rows[k + 1].split(",")[1])
    if tsec(f[2]) > nxt - 0.02: f[2] = ts(max(tsec(f[1]) + 0.3, nxt - 0.02)); rows[k] = ",".join(f); cutn += 1
print("겹친 자막 줄 끝 당김", cutn)
ass += f"Dialogue: 0,{ts(0)},{ts(END)},TOP,,0,0,0,,CINEFLOG\n" + "\n".join(rows) + "\n"
open("subs.ass", "w", encoding="utf-8").write(ass)
if MODE == "subs": sys.exit()

import wave
SR = 48000; N = int((END + 1) * SR)
def load(p):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.float32).reshape(-1, 2)
def save(p, x):
    with wave.open(p, "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
o = subprocess.run(["ffmpeg", "-i", "body.mkv", "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]); g = max(-10, min(14, -17 - I)); print("원본", I, "LUFS → 이득", round(g, 1))
org = np.zeros((N, 2), np.float32); o0 = load("body.mkv")[:N]; org[:len(o0)] = o0 * 10 ** (g / 20)
env = np.ones(N, np.float32); R = int(0.15 * SR)
duck = []
for a, b in NAR:
    if duck and a <= duck[-1][1]: duck[-1][1] = b
    else: duck.append([a, b])
for a, b in duck:                         # 나레 밑 원본 0.2(강의 4강: 나레 겹치는 구간 원본 -25 근처, 완전히 죽이지는 않음)
    ia, ib = max(0, int(a * SR)), min(N, int(b * SR)); env[ia:ib] = 0.2
    env[max(0, ia - R):ia] = np.minimum(env[max(0, ia - R):ia], np.linspace(1, 0.2, ia - max(0, ia - R)))
    env[ib:min(N, ib + R)] = np.minimum(env[ib:min(N, ib + R)], np.linspace(0.2, 1, min(N, ib + R) - ib))
import edges as _e
SW = _e.load_words(CFG.get("words", "src_words.json")); nsd = 0
for w in WN:                              # 나레 없는 액션 조각에 걸린 원본 말소리(자막 없음)는 0.3
    if w["kind"] != "A" or under(w["a"], w["b"]): continue
    L = (w["b"] - w["a"]) * SPD
    if any(w["s"] < x[1] - 0.1 and w["s"] + L > x[0] + 0.1 for x in SW):
        ia, ib = int(w["a"] * SR), int(w["b"] * SR); env[ia:ib] = np.minimum(env[ia:ib], 0.3); nsd += 1
print("말소리 낮춘 액션 조각", nsd)
org *= env[:, None]; save("org.wav", org)
nar = np.zeros((N, 2), np.float32)
for i, t, d, w in narr:
    x = load(w); k = int(t * SR); nar[k:k + len(x)] += x[:N - k]
save("narr_track.wav", nar); save("mix.wav", org + nar)
gate("final", "subs.ass", "narr_track.wav")
t_mus = narr[-1][1] - 1.0
music = os.path.expanduser(CFG.get("music", r"~/volcano_work/달빛롱폼/bgm/Healing.mp3"))
fc = f"[2:a]aresample=48000,atrim=0:{END - t_mus + 1:.2f},volume=0.12,afade=t=in:d=2,afade=t=out:st={END - t_mus - 2:.2f}:d=2,adelay={int(t_mus*1000)}|{int(t_mus*1000)}[mus];" \
     f"[1:a][mus]amix=inputs=2:normalize=0:duration=first,atrim=0:{END:.2f},alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11[a];" \
     f"[0:v]unsharp=5:5:{SHARP}:5:5:0,tpad=stop_mode=clone:stop_duration={OUT:.2f},fade=t=out:st={END - 1:.2f}:d=1,subtitles=subs.ass:fontsdir={FONTS}[v]"
open("fc.txt", "w", encoding="utf-8").write(fc)
subprocess.run(FF + ["-i", "body.mkv", "-i", "mix.wav", "-i", music, "-/filter_complex", "fc.txt", "-map", "[v]", "-map", "[a]",
                     "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "final.mp4.tmp.mp4"], check=True)
os.replace("final.mp4.tmp.mp4", "final.mp4")
o = subprocess.run(["ffmpeg", "-i", "final.mp4", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print("final", round(dur("final.mp4") / 60, 2), "분 · ", re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1], "LUFS")
