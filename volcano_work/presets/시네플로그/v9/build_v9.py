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
FX = CFG.get("fx", False); MOVE, GRAIN = 0.05, 3                                      # ★10-19 사용자 "세 개 다 넣고 견본 보여줘": 조각마다 줌인·줌아웃 번갈아(+5%) · 필름 그레인 → 견본 뒤 "그냥 원래대로 하자" = 기본 끔(ep.json "fx": true 면 켬)
                                                                                     #   테두리 블러(그림 92% + 둘레 흐리게)는 견본 보고 "테두리 블러는 빼자" · 그레인 6 은 파일 5배(3초 10.3MB) → 3(2.3MB, 없을 때 1.9MB)
def vf_fx(k, L):
    if not FX: return f"pad={W}:{H}:0:{BAR}:black,format=yuv420p[vo]"
    z = f"(1+{MOVE}*t/{L:.3f})" if k % 2 == 0 else f"(1+{MOVE}*(1-t/{L:.3f}))"
    return f"scale=w='trunc(1920*{z}/2)*2':h='trunc({SH}*{z}/2)*2':eval=frame,crop=1920:{SH},noise=c0s={GRAIN}:c0f=t,pad={W}:{H}:0:{BAR}:black,format=yuv420p[vo]"
LT = CFG["logo"][3] + 4 if CFG.get("logo") else 0       # ★10-14 01·02 다시 만들기 "로고는 화면키워" — 원본 로고(AYA 등) 아래끝까지 확대로 잘라 냄(ep.json logo=[x0,y0,x1,y1])
def vf_base(z):
    cw = round(1920 / z / 2) * 2; chh = round(SH / z / 2) * 2; yo = min(SH - chh, max((SH - chh) // 2, LT))
    return f"crop={cw}:{chh}:{(1920 - cw) // 2}:{yo},scale=1920:{SH}," + EQ
CLIPS = CFG.get("clips", "clips")
MODE = sys.argv[1] if len(sys.argv) > 1 else "build"
FONTS = CFG.get("fonts", "fonts")
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
def gate(*a):
    r = subprocess.run([sys.executable, os.path.join(HERE, "gate.py"), *a], text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0: sys.exit("관문에 걸림 — 굽지 않는다(위 목록을 고친 뒤 다시)")

WN = json.load(open("windows.json", encoding="utf-8"))
os.makedirs(CLIPS, exist_ok=True)
Y0, HH, X0, WWD = CFG.get("burn", [560, 220, 360, 1200])   # 박힌 자막 자리(burn_detect 와 같은 판정) — 804 높이 영화 기본, 1080 꽉 찬 영화는 ep.json burn
def score(a):
    w = a > 225; d = a < 50; nb = np.zeros_like(w)
    for dy, dx in ((1, 0), (2, 0), (0, 1), (0, 2), (-1, 0), (0, -1)): nb |= np.roll(np.roll(d, dy, 0), dx, 1)
    return int((w & nb).sum())
def top(a):
    r = np.where((a > 225).sum(1) > 4)[0]; return int(Y0 + r.min() * 2) if len(r) else 700
FPS8 = 8
# ★10-17 03 아이 돈 언더스탠드 유 다시: 이탈리아어 구간에만 노란 영어 자막이 박혀 있다(y≈713~742/800) → ep.json "burn_color": "yellow" 면
#   (R+G)/2 − 0.6B 로 바꿔 노랑만 밝게(흰색 ≈102·노랑 ≈255) 본 뒤 같은 잣대(>225 글자 · <50 테두리)로 찾는다.
YEL = "colorchannelmixer=rr=0.5:rg=0.5:rb=-0.6:gr=0.5:gg=0.5:gb=-0.6:br=0.5:bg=0.5:bb=-0.6," if CFG.get("burn_color") == "yellow" else ""
def frames(s0, L):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(s0, 0):.3f}", "-t", f"{L:.3f}", "-i", SRC,
                        "-vf", f"fps={FPS8},crop={WWD}:{HH}:{X0}:{Y0},scale={WWD//2}:{HH//2},{YEL}format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
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
def key(w, k): return f"{w['kind']}_{w['s']:.3f}_{w['b'] - w['a']:.3f}_{int(bool(w.get('noflip')))}_{w.get('rate', 0):.4f}_{w.get('pre', 0):.3f}" + (f"_fx{k % 2}_{MOVE}_{GRAIN}" if FX else "")
def cut(k):
    w = WN[k]; p = f"{CLIPS}/{key(w, k)}.mkv"
    if os.path.exists(p): return p
    f0 = round(w["a"] * FPS); f1 = round(w["b"] * FPS); n = max(1, f1 - f0); L = n / FPS
    act = w["kind"] == "A"; r = w.get("rate", SPD if act else 1.0); sl = L * r; s0 = w["s"] - w.get("pre", 0)
    flip = not w.get("noflip")
    bs = burn(s0, sl)
    ch = ["[0:v]" + (f"setpts=PTS/{r:.4f}," if r != 1 else "") + "split=%d[b]" % (1 + len(bs)) + "".join(f"[z{i}]" for i in range(len(bs))), f"[b]{vf_base(ZOOM if flip else ZOOM_NF)}[v0]"]
    for i, (a, b, tp) in enumerate(bs):
        h = max(540, min(SH - 104, tp - 12)) - LT; ww = round(1920 * h / SH / 2) * 2     # 위는 로고 아래부터(LT)
        a2, b2 = a / r, b / r
        ch.append(f"[z{i}]crop={ww}:{h}:{(1920 - ww) // 2}:{LT},scale=1920:{SH},{EQ}[zz{i}]")
        ch.append(f"[v{i}][zz{i}]overlay=0:0:enable='between(t,{max(0, a2 - 0.1):.3f},{b2 + 0.1:.3f})'[v{i + 1}]")
    ch.append(f"[v{len(bs)}]" + ("hflip," if flip else "") + vf_fx(k, L))
    subprocess.run(FF + ["-ss", f"{max(s0, 0):.4f}", "-i", SRC, "-frames:v", str(n), "-filter_complex", ";".join(ch), "-map", "[vo]", "-map", "0:a:0",
                         "-af", (f"atempo={r:.4f}," if not act and r != 1 else "") + f"apad,atrim=0:{L:.5f},afade=t=in:d=0.03,afade=t=out:st={max(0, L - 0.05):.3f}:d=0.05,aresample=48000",
                         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "pcm_s16le", "-ac", "2", "-r", "24000/1001", p + ".tmp.mkv"], check=True)
    os.replace(p + ".tmp.mkv", p)
    return p
if MODE == "cut":
    gate("pre")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(int(os.environ.get("CUT_JOBS", 6))) as ex: ps = list(ex.map(cut, range(len(WN))))   # 10-20 메모리 부족(13.9GB PC)으로 멈춤 → CUT_JOBS=3
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
NF = CFG.get("nfont") or ["GyeonggiTitle", "GyeonggiTitleB.ttf", -1]; DF = CFG.get("dfont") or ["Stylish", "Stylish.ttf", -1]   # ★10-16 편마다 자막 글꼴 [ASS 이름, fonts 안 파일, 기울임 -1|0] — 04v2 사용자 "글자체들은 원래프리셋대로해줘"(영화리뷰롱폼 글꼴)
NSZ = 100; FN = ImageFont.truetype(f"{FONTS}/{NF[1]}", NSZ); MAXW = 1300
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
ev = []; snapped = 0; evn = []          # evn = 덩어리마다 나레 번호(지무비식 자막이 강조 말을 찾는다)
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
        ev.append((a2, max(b2, a2 + 0.3), s)); evn.append(i)
print("목소리 시작에 맞춘 나레 자막 줄", snapped)

# ★10-16 04v2 지무비식 자막(ep.json "capstyle": "jimovie") — 사용자 "글자가 내가새로준 지침에 보면 큰글자도있고 색깔있는글자도 있고 다양한데 넌 그걸안지켰네?"
#   영화리뷰롱폼 엔진(presets/영화리뷰롱폼 builders/text_layout·caption_stream)의 꼴: 일반 나레 = 흰 카페24당당해 작게(사장님 b29 58px),
#   핵심 말이 든 나레 = 줄 전체 디스플레이(잉크 118, 흰 부분 본명조) + 그 말만 감정 글꼴·색(TONE_FONT), 짧은 결정타 = 펀치(잉크 158),
#   대사 = 광화문(잉크 54), 핵심 대사 몇 줄 = 줄 전체 노랑 크게. 강조할 말·감정은 작업 폴더 emph.json(나레 번호 → [말, 감정]).
JM = CFG.get("capstyle") == "jimovie"
from jm_style import JM_FONTS, JM_TONE, JM_GRAD, JM_INK, JM_W   # 글꼴·감정·색·크기 표는 jm_style.py 한 곳(캡컷 capcut_font.py 도 읽는다)
def jm_c(rgb): return "&H00%02X%02X%02X&" % (rgb[2], rgb[1], rgb[0])
def jm_fs(key, ink): return round(ink * 100 / JM_FONTS[key][2])
_jm_pil = {}
def jm_w(key, size, t):
    k = (key, size)
    if k not in _jm_pil: _jm_pil[k] = ImageFont.truetype(f"{FONTS}/{JM_FONTS[key][0]}", size)
    return _jm_pil[k].getlength(t)
JM_POP = r"{\fscx72\fscy72\t(0,110,\fscx108\fscy108)\t(110,190,\fscx100\fscy100)}"
def jm_span(s, p):
    """자막 덩어리 s 안에서 강조 말 p 가 걸친 자리 (i0, i1) — 덩어리 경계에 걸리면 걸친 쪽만(2자 이상)"""
    if p in s: i = s.index(p); return i, i + len(p)
    for L in range(min(len(s), len(p)) - 1, 1, -1):
        if s.endswith(p[:L]): return len(s) - L, len(s)
        if s.startswith(p[-L:]): return 0, L
    return None
def jm_nar(s, p, tone, n_emph):
    sp = jm_span(s, p) if p else None
    if not sp: return "NP", s
    i0, i1 = sp; key, rgb, ital = JM_TONE[tone]
    if tone == "emotion" and n_emph % 2: key = "성경"
    if rgb is None: rgb = JM_GRAD[n_emph % len(JM_GRAD)]
    segs = [(s[:i0], "본명조", None, 0), (s[i0:i1], key, rgb, ital), (s[i1:], "본명조", None, 0)]
    core = len(s[i0:i1].replace(" ", "")); allc = len(s.replace(" ", ""))
    ink = JM_INK["punch"] if core >= 0.8 * allc and allc <= 9 else JM_INK["emph"]
    sizes = [jm_fs(k, ink) for _, k, _, _ in segs]
    w = sum(jm_w(k, z, t) for (t, k, _, _), z in zip(segs, sizes) if t)
    if w > JM_W: sizes = [max(30, int(z * JM_W / w)) for z in sizes]
    out = JM_POP
    for (t, k, c, it), z in zip(segs, sizes):
        if t: out += "{\\fn%s\\fs%d\\c%s\\i%d}%s" % (JM_FONTS[k][1], z, jm_c(c) if c else "&H00FDFDFC&", it, t)
    return "NE", out
if JM:
    EMPH = json.load(open(CFG.get("emph", "emph.json"), encoding="utf-8")); EN = EMPH.get("n", {}); DY = EMPH.get("dlg_yellow", [])
    evj = []; ne = 0
    for (a, b, s), i in zip(ev, evn):
        p, tone = EN.get(str(i), [None, None]); st_, txt = jm_nar(s, p, tone, ne)
        if st_ == "NE": ne += 1
        evj.append((a, b, txt, st_))
    print("지무비식 나레 자막: 강조", ne, "/", len(evj))

JM_STYLES = (f"Style: NP,{JM_FONTS['카페24당당해'][1]},{jm_fs('카페24당당해', JM_INK['plain'])},&H00FDFDFC,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,-1,0,1,2,4,2,60,60,165,1\n"
             f"Style: NE,{JM_FONTS['본명조'][1]},{jm_fs('본명조', JM_INK['emph'])},&H00FDFDFC,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,6,3,2,40,40,165,1\n"
             f"Style: DJ,{JM_FONTS['광화문'][1]},{jm_fs('광화문', JM_INK['dlg'])},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,2,2,60,60,165,1\n"
             f"Style: DY,{JM_FONTS['광화문'][1]},{jm_fs('광화문', JM_INK['dlg_y'])},&H0000E7FE,&H0000E7FE,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,3,2,60,60,165,1\n") if JM else ""
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: N,{NF[0]},{NSZ},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,{NF[2]},0,0,100,100,0,0,1,5,1,2,60,60,165,1
Style: D,{DF[0]},104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,{DF[2]},0,0,100,100,0,0,1,5,1,2,60,60,165,1
{JM_STYLES}Style: TOP,Noto Sans KR Black,104,&H00B5B5B5,&H00B5B5B5,&H00000000,&H64000000,-1,-1,0,0,100,100,0,0,1,4,0,9,40,40,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
rows = [f"Dialogue: 0,{ts(a)},{ts(b)},{st_},,0,0,0,,{s}" for a, b, s, st_ in evj] if JM else [f"Dialogue: 0,{ts(a)},{ts(b)},N,,0,0,0,,{s}" for a, b, s in ev]
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
    for p, a0, b0 in parts:
        if JM and any(y in p for y in DY): rows.append(f"Dialogue: 0,{ts(a0)},{ts(max(b0, a0 + 0.6))},DY,,0,0,0,,{JM_POP}{p}")
        else: rows.append(f"Dialogue: 0,{ts(a0)},{ts(max(b0, a0 + 0.6))},{'DJ' if JM else 'D'},,0,0,0,,{p}")
    nd += 1
print("대사 창 자막", nd)
rows.sort(key=lambda r: tsec(r.split(",")[1])); cutn = 0
for k in range(len(rows) - 1):           # 두 줄 겹침 없게: 앞 줄은 다음 줄 뜨기 0.02초 전에 끈다
    f = rows[k].split(",", 9); nxt = tsec(rows[k + 1].split(",")[1])
    if tsec(f[2]) > nxt - 0.02: f[2] = ts(max(tsec(f[1]) + 0.3, nxt - 0.02)); rows[k] = ",".join(f); cutn += 1
    if tsec(f[2]) > nxt - 0.02:          # ★10-14 02 패밀리 플랜: 「뭐?」「응」 같은 0.3초 줄은 더 못 줄인다 → 다음 줄을 0.02초 뒤로 민다(관문 ⑪)
        g = rows[k + 1].split(",", 9); g[1] = ts(tsec(f[2]) + 0.02)
        if tsec(g[2]) < tsec(g[1]) + 0.3: g[2] = ts(tsec(g[1]) + 0.3)
        rows[k + 1] = ",".join(g)
print("겹친 자막 줄 끝 당김", cutn)
# ★10-20 무드킹식 인물 이름표 — 사용자 "https://www.youtube.com/watch?v=fK2xpgBdMJM 이영상 봐봐." · "인물소개 잘해놨어"
#   인물이 처음 나오는 줄(script 옵션 {"tag": "이름"} 또는 {"tag": ["이름", "관계"]})의 첫 조각에, 얼굴 옆(가슴 높이) 노란 굵은 이름(잘난체 2)을 그 조각 동안(최대 3초).
#   자리는 body.mkv 그 조각 가운데 프레임의 얼굴(OpenCV) — 얼굴이 왼쪽이면 오른쪽에, 오른쪽이면 왼쪽에. 못 찾으면 왼쪽 아래. 손으로 고칠 땐 ep.json "tag_pos": {"이름": [x, y]}.
TAGF = ["Jalnan 2 TTF", "Jalnan2TTF.ttf"]; TAGS = []
#   ★시네플로그는 이름표를 넣지 않는다(10-20 사용자 "우리는 인물 이름표는 넣지마") — ep.json "name_tag": true 인 편만(대본에 tag 가 있어도 무시)
if CFG.get("name_tag") and any(w.get("tag") for w in WN):
    import cv2, shutil as _sh
    if not os.path.exists(f"{FONTS}/{TAGF[1]}"): _sh.copy2(os.path.expanduser(f"~/AppData/Local/Microsoft/Windows/Fonts/{TAGF[1]}"), f"{FONTS}/{TAGF[1]}")
    # 얼굴 찾기 = YuNet(models/yunet.onnx, 다른 프리셋에 있던 것) — OpenCV 5.0 엔 Haar 가 없고, 한글 경로는 못 읽어 바이트로 넣는다
    _det = cv2.FaceDetectorYN.create("onnx", np.frombuffer(open(os.path.join(HERE, "..", "models", "yunet.onnx"), "rb").read(), np.uint8), np.array([], np.uint8), (960, 540), 0.7)
    def _face(t):
        b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", "body.mkv", "-frames:v", "1", "-vf", "scale=960:540", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
        if len(b) < 960 * 540 * 3: return None
        _, fs = _det.detect(np.frombuffer(b[:960 * 540 * 3], np.uint8).reshape(540, 960, 3))
        if fs is None or not len(fs): return None
        x, y, w_, h_ = max(fs, key=lambda f: f[2] * f[3])[:4]
        return (x * 2, y * 2, w_ * 2, h_ * 2)
    TPOS = CFG.get("tag_pos", {})
    for k in sorted({w["k"] for w in WN if w.get("tag")}):
        ws = [w for w in WN if w["k"] == k]; w = ws[min(ws[0].get("tag_w", 0), len(ws) - 1)]   # "tag_w" = 그 줄 몇 번째 조각에(이름을 말하는 조각, 기본 첫 조각)
        tg = w["tag"]; name, rel = (tg, None) if isinstance(tg, str) else (tg[0], tg[1] if len(tg) > 1 else None)
        a0 = w["a"] + 0.1; b0 = min(w["b"], w["a"] + 3.0); tw = len(name) * 92
        if name in TPOS: x, y = TPOS[name]
        else:
            f = _face((w["a"] + w["b"]) / 2)
            if f:
                fx, fy, fw, fh = f
                x = min(1920 - tw / 2 - 50, fx + fw + 70 + tw / 2) if fx + fw / 2 < 960 else max(tw / 2 + 50, fx - 70 - tw / 2)
                y = min(760, max(300, fy + fh * 1.05))
            else: x, y = 60 + tw / 2, 640
        txt = name + (r"\N{\fs58}(" + rel + ")" if rel else "")
        TAGS.append(f"Dialogue: 1,{ts(a0)},{ts(b0)},TAG,,0,0,0,,{{\\pos({x:.0f},{y:.0f})\\fad(120,150)\\fscx80\\fscy80\\t(0,120,\\fscx106\\fscy106)\\t(120,200,\\fscx100\\fscy100)}}{txt}")
    print("인물 이름표", len(TAGS), [t.split("}")[-1] for t in TAGS])
    ass = ass.replace("\n[Events]", f"Style: TAG,{TAGF[0]},96,&H004ADCFF,&H004ADCFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,5,2,5,0,0,0,1\n\n[Events]", 1)
# 오른쪽 위 글자 = ep.json "brand"(이 PC 기본 CINEFLOG). ★다른 PC 10-19 사용자 "이채널은 시네플로그라고 하지말고 대작이라고 해줘" → 그 PC 는 「대작」(10-20 이 PC 로 가져올 때 기본은 그대로 둠)
ass += f"Dialogue: 0,{ts(0)},{ts(END)},TOP,,0,0,0,,{CFG.get('brand', 'CINEFLOG')}\n" +"\n".join(rows + TAGS) + "\n"
open("subs.ass", "w", encoding="utf-8").write(ass)
# ★다른 PC 10-20 사용자 "그리고 대작 워터마크 무드킹처럼 만들어" → 워터마크 그림(brand/make_watermark.py)을 오른쪽 위에 얹고, 화면에 굽는 자막(subs_burn.ass)엔 TOP 글자를 뺀다
#   (TOP 줄은 캡컷용으로 subs.ass 에 남김). 이 PC 는 ep.json "brand_png": "대작_워터마크.png"(brand/ 안 이름 또는 절대 경로)를 적은 편만 — 없으면 옛 글자.
WM = CFG.get("brand_png") or None
if WM and not os.path.isabs(WM): WM = os.path.join(HERE, "..", "brand", WM)
if WM and not os.path.exists(WM): WM = None
open("subs_burn.ass", "w", encoding="utf-8").write("".join(l for l in ass.splitlines(True) if not (WM and l.startswith("Dialogue") and ",TOP," in l)))
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
QG = CFG.get("quiet_gain", 0.35); nq = 0          # ★10-14 유명 노래 구간(ep.json quiet = 원본 초 [[a,b],…]) — 그 원본을 쓴 조각은 원본 소리를 더 낮춤(음악 저작권 소리 판정 피하기)
for w in WN:
    L = (w["b"] - w["a"]) * w.get("rate", SPD if w["kind"] == "A" else 1.0); s0 = w["s"] - w.get("pre", 0)
    if any(s0 < b and s0 + L > a for a, b in CFG.get("quiet", [])):
        ia, ib = int(w["a"] * SR), int(w["b"] * SR); env[ia:ib] *= QG; nq += 1
print("노래 구간이라 원본 소리 더 낮춘 조각", nq)
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
     f"[0:v]unsharp=5:5:{SHARP}:5:5:0,tpad=stop_mode=clone:stop_duration={OUT:.2f},fade=t=out:st={END - 1:.2f}:d=1,subtitles=subs_burn.ass:fontsdir={FONTS}" + \
     ("[vs];[3:v]format=rgba[wm];[vs][wm]overlay=W-w-72:54[v]" if WM else "[v]")   # 10-20 텔레그램 "아래 왼쪽으로 조금 옮겨" (40:28 → 72:54)
open("fc.txt", "w", encoding="utf-8").write(fc)
subprocess.run(FF + ["-i", "body.mkv", "-i", "mix.wav", "-i", music] + (["-i", WM] if WM else []) + ["-/filter_complex", "fc.txt", "-map", "[v]", "-map", "[a]",
                     "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "final.mp4.tmp.mp4"], check=True)
os.replace("final.mp4.tmp.mp4", "final.mp4")
def lufs(p):
    o = subprocess.run(["ffmpeg", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]), max(float(x) for x in re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o)[-2:])
I, TP = lufs("final.mp4")
if abs(I + 16) > 0.3 or TP > -1.0:        # ★10-14 README 「소리 맞춤」을 굽기 안으로: loudnorm 한 번으로는 -16.3·정점 +1.8 → 영상 복사 + 소리만(alimiter 는 level=disabled 필수)
    subprocess.run(FF + ["-i", "final.mp4", "-c:v", "copy", "-af", f"aresample=192000,volume={-16 - I:.2f}dB,alimiter=limit=0.8:level=disabled:attack=1:release=60,aresample=48000",
                         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "final_lv.mp4"], check=True)
    os.replace("final_lv.mp4", "final.mp4"); print("소리 맞춤", I, TP, "→", *lufs("final.mp4"))
    I2, TP2 = lufs("final.mp4")
    if TP2 > -1.0:                        # ★10-14 01 헤즈 오브 스테이트: limit 0.8 로도 AAC 뒤 정점 -0.2 → limit 0.7 로 한 번 더(-16.1·-2.3)
        subprocess.run(FF + ["-i", "final.mp4", "-c:v", "copy", "-af", f"aresample=192000,volume={-16 - I2 + 0.2:.2f}dB,alimiter=limit=0.7:level=disabled:attack=1:release=60,aresample=48000",
                             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "final_lv.mp4"], check=True)
        os.replace("final_lv.mp4", "final.mp4"); print("소리 맞춤 2", I2, TP2, "→", *lufs("final.mp4"))
print("final", round(dur("final.mp4") / 60, 2), "분 · ", *lufs("final.mp4"), "LUFS·정점")
