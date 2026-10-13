# -*- coding: utf-8 -*-
"""16 핀치 v5 — 벤치(w-nMnsl6L1A) 편집표(edl.json) 그대로 원본을 이어 붙이고, 벤치 나레 자리(bench_spans.json)에 우리 나레(narr/nNNN).
- 화면: 원본 1920x804 그대로 가운데(위아래 검은 띠 138), 벤치처럼 좌우반전·확대 없음(벤치 flip 컷만 반전).
- 소리: 원본 소리, 우리 나레가 나오는 동안만 원본을 낮춘다(-14dB). 끝 비평 아래 음악. 최종 -16 LUFS.
- 자막: 나레만(박힌 한국어 대사 자막은 원본 그림에 있음) — 경기천년제목 100, 아래 검은 띠 안. CINEFLOG 오른쪽 위.
- mp4 4K 비슷한 선명(unsharp). 캡컷은 capcut_style04(4K 0.50).
사용: python build_v5.py cut → clips_v5/ · python build_v5.py → final.mp4"""
import json, math, os, subprocess, sys
FF = ["ffmpeg", "-v", "error", "-y"]
SRC = "../ep16v4_핀치/src.mp4"; FPS = 24000 / 1001
W, H, BAR = 1920, 1080, 138
E = json.load(open("edl.json")); SP = json.load(open("bench_spans.json", encoding="utf-8"))
SKIP = {119}   # 118·119 녹음 경계가 어긋나 118 에 합침
MODE = sys.argv[1] if len(sys.argv) > 1 else "build"
os.makedirs("clips_v5", exist_ok=True)
def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

# 컷: 벤치 시간축 프레임 경계로 → 누적 어긋남 0
segs = []
for k, e in enumerate(E):
    f0 = round(e["b0"] * FPS); f1 = round((e["b0"] + e["d"]) * FPS)
    if f1 > f0: segs.append((k, f0, f1, e["s0"] + (f0 / FPS - e["b0"]), e["flip"]))
def cut(a):
    k, f0, f1, s0, flip = a; p = f"clips_v5/c{k:04d}.mkv"
    if os.path.exists(p): return p
    n = f1 - f0; L = n / FPS
    vf = ("hflip," if flip else "") + f"pad={W}:{H}:0:{BAR}:black,format=yuv420p"
    subprocess.run(FF + ["-ss", f"{max(s0, 0):.4f}", "-i", SRC, "-frames:v", str(n), "-vf", vf,
                         "-af", f"apad,atrim=0:{L:.5f},aresample=48000", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                         "-c:a", "pcm_s16le", "-ac", "2", "-r", "24000/1001", p], check=True)
    return p
if MODE == "cut":
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as ex: ps = list(ex.map(cut, segs))
    open("all_v5.txt", "w").write("".join(f"file '{p}'\n" for p in ps))
    subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", "all_v5.txt", "-c", "copy", "body_v5.mkv"], check=True)
    print("컷", len(ps), "· 몸통", round(dur("body_v5.mkv"), 2), "초 (벤치 1616.5)"); sys.exit()

BODY = dur("body_v5.mkv")
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
END = max(BODY, narr[-1][1] + narr[-1][2] + 1.5); OUT = END - BODY

# 원본 낮추기 구간(앞뒤 0.25초 여유) → volume 식
duck = []
for _, t, d, _ in narr:
    a, b = t - 0.25, t + d + 0.3
    if duck and a <= duck[-1][1]: duck[-1][1] = b
    else: duck.append([a, b])
# expr = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in duck)
# 원본 소리 크기: 몸통 전체를 -17 LUFS 로 맞추는 이득
o = subprocess.run(["ffmpeg", "-i", "body_v5.mkv", "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
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
Style: N,GyeonggiTitle,{NS},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,-1,0,0,100,100,0,0,1,5,1,2,60,60,22,1
Style: TOP,Noto Sans KR Black,104,&H00B5B5B5,&H00B5B5B5,&H00000000,&H64000000,-1,-1,0,0,100,100,0,0,1,4,0,9,40,40,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0)},{ts(END)},TOP,,0,0,0,,CINEFLOG
"""
for a, b, s in ev: ass += f"Dialogue: 0,{ts(a)},{ts(b)},N,,0,0,0,,{s}\n"
open("subs_v5.ass", "w", encoding="utf-8").write(ass)
json.dump([{"ni": i, "t": round(t, 3), "d": round(d, 3)} for i, t, d, _ in narr], open("narr_place.json", "w"), indent=0)

# 소리: numpy 로 원본(이득·나레 자리 낮춤, 0.15초 경사) + 나레를 섞어 mix_v5.wav, 원본만 낮춘 것은 org_v5.wav(캡컷용)
import numpy as np, wave
SR = 48000; N = int((END + 1) * SR)
def load(p):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.float32).reshape(-1, 2)
def save(p, x):
    with wave.open(p, "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
org = np.zeros((N, 2), np.float32); o0 = load("body_v5.mkv")[:N]; org[:len(o0)] = o0 * 10 ** (g / 20)
env = np.ones(N, np.float32); R = int(0.15 * SR)
for a, b in duck:
    ia, ib = max(0, int(a * SR)), min(N, int(b * SR)); env[ia:ib] = 0.2
    env[max(0, ia - R):ia] = np.minimum(env[max(0, ia - R):ia], np.linspace(1, 0.2, ia - max(0, ia - R)))
    env[ib:min(N, ib + R)] = np.minimum(env[ib:min(N, ib + R)], np.linspace(0.2, 1, min(N, ib + R) - ib))
org *= env[:, None]; save("org_v5.wav", org)
nar = np.zeros((N, 2), np.float32)
for i, t, d, w in narr:
    x = load(w); k = int(t * SR); nar[k:k + len(x)] += x[:N - k]
save("narr_track.wav", nar); save("mix_v5.wav", org + nar)
t_mus = narr[-1][1] - 1.0
music = os.path.expanduser(r"~/volcano_work/달빛롱폼/bgm/") + "Healing.mp3"
inputs = ["-i", "body_v5.mkv", "-i", "mix_v5.wav", "-i", music]
fc = f"[2:a]aresample=48000,atrim=0:{END - t_mus + 1:.2f},volume=0.12,afade=t=in:d=2,afade=t=out:st={END - t_mus - 3:.2f}:d=3,adelay={int(t_mus*1000)}|{int(t_mus*1000)}[mus];" \
     f"[1:a][mus]amix=inputs=2:normalize=0:duration=first,atrim=0:{END:.2f},alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11[a];" \
     f"[0:v]unsharp=5:5:0.55:5:5:0,tpad=stop_mode=add:stop_duration={OUT:.2f}:color=black,subtitles=subs_v5.ass:fontsdir=../ep16v4_핀치/fonts[v]"
open("fc_v5.txt", "w", encoding="utf-8").write(fc)
subprocess.run(FF + inputs + ["-/filter_complex", "fc_v5.txt", "-map", "[v]", "-map", "[a]",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                              "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "final_v5.mp4"], check=True)
print("final_v5", round(dur("final_v5.mp4") / 60, 2), "분")
