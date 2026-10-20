# -*- coding: utf-8 -*-
"""영화 리뷰 쇼츠 굽기(다른 PC 「대작」에서 10-20 가져옴 — 오른쪽 위 글자는 ep.json "brand", 기본 CINEFLOG · 완성본은 final_dir.FINAL) — 10-20 사용자 "아니야. 이템플릿으로 할거야. 그건 다른채널이야".
순서(쇼츠 작업 폴더 = 롱폼 작업 폴더 안 shortsNN): shorts_setup.py → plan_v9.py → narr_pic.py → build_v9.py cut(관문 pre·조각·body.mkv) → 이것.
- 화면: 템플릿 위·아래 띠(shorts_tpl.make_frame — 제목 두 줄·「대작」) + 가운데 1080x1072 = 조각(1920x1080)을 세로로 꽉 차게 잘라 넣음.
  자르는 자리는 조각마다 얼굴 가운데(OpenCV 얼굴 찾기, 없으면 화면 가운데) — crop.json, 손으로 고칠 땐 crop_fix.json {"조각 번호": 가운데x(0~1920)}.
- 자막: 영상 자리 아래쪽 한 줄(Pretendard Black, 템플릿 견본 70 크기 = ASS 84), 나레 흰색 · 원음 대사 번역 노랑. 쉼표·마침표 없음, 한 줄에 다 안 들어가면 띄어쓰기에서 나눠 차례로.
- 소리: build_v9 와 같은 섞기(원본 -17 LUFS · 나레 밑 0.2 · 말소리 걸린 액션 조각 0.3 · 노래 구간 더 낮춤) + 나레(1.35배) · 음악 없음 · 최종 -16 LUFS.
- 굽기 직전 관문 final(나레 자막 ↔ 목소리 · 자막 겹침). 다 되면 영화리뷰 최종본/<이름>.mp4 로 복사하고 확인용 프레임 시트(_시트.jpg)를 만든다.
사용: python build_shorts.py "제목 윗줄" "제목 아랫줄" <완성본 이름(예: 03_웨어더하트이즈_쇼츠1)>"""
import json, os, re, shutil, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, ".."), os.path.join(HERE, "..", "v9")]
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageFont
from shorts_tpl import make_frame, W, H, FONT
from final_dir import FINAL
import edges as EDG
TITLE, NAME = sys.argv[1:3], sys.argv[3]
FF = ["ffmpeg", "-v", "error", "-y"]
CFG = json.load(open("ep.json", encoding="utf-8")); WN = json.load(open("windows.json", encoding="utf-8")); PL = json.load(open("narr_place.json"))
SPD = 1.05
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
BODY = dur("body.mkv")
narr = [(q["ni"], q["t"], dur(f"narr/n{q['ni']:03d}.wav"), f"narr/n{q['ni']:03d}.wav") for q in PL]
END = max(BODY, narr[-1][1] + narr[-1][2] + 0.3)

# ── 틀
frame, MY0, MY1 = make_frame(title=TITLE, brand=CFG.get("brand", "CINEFLOG"), wm=CFG.get("brand_png")); MH = MY1 - MY0
frame.save("_frame.png")
CW = round(W * 1080 / MH / 2) * 2                       # 조각(1920x1080)에서 잘라 낼 폭 → 1080x1072 로 줄임

# ── 조각마다 자르는 자리(얼굴 가운데)
import cv2
DET = cv2.FaceDetectorYN.create("onnx", np.frombuffer(open(os.path.join(HERE, "..", "models", "yunet.onnx"), "rb").read(), np.uint8), np.array([], np.uint8), (960, 540), 0.7)   # OpenCV 5.0 엔 Haar 없음 · 한글 경로라 바이트로
def face_cx(t):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", "body.mkv", "-frames:v", "1", "-vf", "scale=960:540", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    if len(b) < 960 * 540 * 3: return None
    _, fs = DET.detect(np.frombuffer(b[:960 * 540 * 3], np.uint8).reshape(540, 960, 3))
    if fs is None or not len(fs): return None
    f = max(fs, key=lambda f: f[2] * f[3]); return float(f[0] + f[2] / 2) * 2
CROP = json.load(open("crop.json")) if os.path.exists("crop.json") else {}
for i, w in enumerate(WN):
    if str(i) not in CROP: CROP[str(i)] = face_cx((w["a"] + w["b"]) / 2)
json.dump(CROP, open("crop.json", "w"), indent=0)
FIX = json.load(open("crop_fix.json")) if os.path.exists("crop_fix.json") else {}
xs = []
for i, w in enumerate(WN):
    cx = FIX.get(str(i), CROP[str(i)]); cx = 960 if cx is None else cx
    xs.append(int(min(1920 - CW, max(0, cx - CW / 2)) // 2 * 2))
print("자르는 자리: 얼굴 찾음", sum(1 for v in CROP.values() if v is not None), "/", len(WN), "· 손으로 고침", len(FIX))
xe = f"{xs[0]}" + "".join(f"+({xs[i] - xs[i - 1]})*gte(t,{WN[i]['a']:.3f})" for i in range(1, len(WN)) if xs[i] != xs[i - 1])

# ── 무드킹식 인물 이름표(롱폼 build_v9 와 같은 script 옵션 {"tag": …, "tag_w": n}) — 얼굴 옆에, 쇼츠 화면 좌표로 옮겨서
def face_box(t):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", "body.mkv", "-frames:v", "1", "-vf", "scale=960:540", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    if len(b) < 960 * 540 * 3: return None
    _, fs = DET.detect(np.frombuffer(b[:960 * 540 * 3], np.uint8).reshape(540, 960, 3))
    if fs is None or not len(fs): return None
    f = max(fs, key=lambda f: f[2] * f[3]); return [float(v) * 2 for v in f[:4]]
TAGS = []; SC = W / CW
for k in (sorted({w["k"] for w in WN if w.get("tag")}) if CFG.get("name_tag") else []):   # ★시네플로그는 이름표 안 넣음(10-20 "우리는 인물 이름표는 넣지마")
    ii = [i for i, w in enumerate(WN) if w["k"] == k]; i = ii[min(WN[ii[0]].get("tag_w", 0), len(ii) - 1)]; w = WN[i]
    tg = w["tag"]; name, rel = (tg, None) if isinstance(tg, str) else (tg[0], tg[1] if len(tg) > 1 else None)
    tw = len(name) * 92; f = face_box((w["a"] + w["b"]) / 2)
    if f:
        fx, fy, fw, fh = f; cx = (fx + fw / 2 - xs[i]) * SC
        x = min(W - tw / 2 - 30, cx + fw * SC / 2 + 50 + tw / 2) if cx < W / 2 else max(tw / 2 + 30, cx - fw * SC / 2 - 50 - tw / 2)
        y = MY0 + min(760, max(220, fy + fh * 1.05)) * MH / 1080
    else: x, y = 30 + tw / 2, MY0 + MH * 0.55
    TAGS.append((w["a"] + 0.1, min(w["b"], w["a"] + 3.0), name + (r"\N{\fs56}(" + rel + ")" if rel else ""), x, y))

# ── 자막
FN = ImageFont.truetype(FONT, 70); MAXW = 1000
def wid(s): return FN.getlength(s)
def clean(s): return re.sub(r"\s+", " ", re.sub(r"[,.…]", "", s)).strip()
def split_fit(s):
    """한 줄에 안 들어가면 가운데에 가까운 띄어쓰기에서 나눈다(두 줄 금지 — 차례로 띄움)"""
    if wid(clean(s)) <= MAXW or " " not in s.strip(): return [s]
    sp = [m.start() for m in re.finditer(" ", s)]; k = min(sp, key=lambda p: abs(p - len(s) / 2))
    return split_fit(s[:k]) + split_fit(s[k + 1:])
rows = []
for ni, t, d, _ in narr:
    j = json.load(open(f"narr/n{ni:03d}.json", encoding="utf-8")); text = "".join(j["chars"]); st, en = j["st"], j["en"]
    pieces = []; c0 = 0
    for m in re.finditer(r"[,.?!]+", text):
        pieces.append((c0, m.end())); c0 = m.end()
    if c0 < len(text): pieces.append((c0, len(text)))
    cards = []
    for a, b in pieces:
        seg = text[a:b]; pos = a
        for p in split_fit(seg):
            k = text.find(p, pos); pos = k + len(p)
            k0 = k + (len(p) - len(p.lstrip()))
            if clean(p): cards.append((clean(p), st[min(k0, len(st) - 1)]))
    for n, (s, a) in enumerate(cards):
        b = cards[n + 1][1] - 0.02 if n + 1 < len(cards) else min(d + 0.1, en[-1] + 0.25)
        rows.append((t + a, t + max(b, a + 0.3), "N", s))
for w in WN:
    if w["kind"] != "D": continue
    pre, rr = w.get("pre", 0), w.get("rate", 1.0)
    if "subs" in w: parts = [(p, w["a"] + (a + pre) / rr, w["a"] + (b + pre) / rr) for p, a, b in w["subs"]]
    else:
        ps = w["ko"].split(" / "); s0, e1 = 0.05, w.get("sub1", w["b"] - w["a"] - 0.05); tot = sum(len(p) for p in ps); acc = 0; parts = []
        for p in ps:
            a0 = w["a"] + (s0 + (e1 - s0) * acc / tot + pre) / rr; acc += len(p); parts.append((p, a0, w["a"] + (s0 + (e1 - s0) * acc / tot + pre) / rr))
    for p, a0, b0 in parts:
        for q in split_fit(p): rows.append((a0, max(b0, a0 + 0.6), "D", clean(q)))
rows.sort()
for k in range(len(rows) - 1):           # 두 줄 겹침 없게
    a, b, st_, s = rows[k]; nxt = rows[k + 1][0]
    if b > nxt - 0.02: rows[k] = (a, max(a + 0.3, nxt - 0.02), st_, s)
    if rows[k][1] > nxt - 0.02: rows[k + 1] = (rows[k][1] + 0.02, max(rows[k + 1][1], rows[k][1] + 0.32), rows[k + 1][2], rows[k + 1][3])
def ts(x): return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
MV = H - MY1 + 70
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: N,Pretendard Black,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,7,0,2,30,30,{MV},1
Style: D,Pretendard Black,84,&H005CE4FF,&H005CE4FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,7,0,2,30,30,{MV},1
Style: TAG,Jalnan 2 TTF,96,&H004ADCFF,&H004ADCFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,5,2,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "".join(f"Dialogue: 0,{ts(a)},{ts(b)},{st_},,0,0,0,,{s}\n" for a, b, st_, s in rows) \
    + "".join(f"Dialogue: 1,{ts(a)},{ts(b)},TAG,,0,0,0,,{{\\pos({x:.0f},{y:.0f})\\fad(120,150)\\fscx80\\fscy80\\t(0,120,\\fscx106\\fscy106)\\t(120,200,\\fscx100\\fscy100)}}{s}\n" for a, b, s, x, y in TAGS)
open("subs_shorts.ass", "w", encoding="utf-8").write(ass)
os.makedirs("fonts_shorts", exist_ok=True); shutil.copy2(FONT, "fonts_shorts/")
if TAGS: shutil.copy2(os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/Jalnan2TTF.ttf"), "fonts_shorts/")
print("인물 이름표", len(TAGS), [t[2] for t in TAGS])
print("자막", len(rows), "줄 (나레", sum(1 for r in rows if r[2] == "N"), "· 대사", sum(1 for r in rows if r[2] == "D"), ")")

# ── 소리 (build_v9 와 같은 섞기, 음악 없음)
import wave
SR = 48000; N = int((END + 1) * SR)
def load(p):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.float32).reshape(-1, 2)
def save(p, x):
    with wave.open(p, "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
o = subprocess.run(["ffmpeg", "-i", "body.mkv", "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]); g = max(-10, min(14, -17 - I))
org = np.zeros((N, 2), np.float32); o0 = load("body.mkv")[:N]; org[:len(o0)] = o0 * 10 ** (g / 20)
NAR = [(t - 0.25, t + d + 0.25) for _, t, d, _ in narr]
def under(a, b): return any(a < y and b > x for x, y in NAR)
env = np.ones(N, np.float32); R = int(0.15 * SR); duck = []
for a, b in NAR:
    if duck and a <= duck[-1][1]: duck[-1][1] = b
    else: duck.append([a, b])
for a, b in duck:
    ia, ib = max(0, int(a * SR)), min(N, int(b * SR)); env[ia:ib] = 0.2
    env[max(0, ia - R):ia] = np.minimum(env[max(0, ia - R):ia], np.linspace(1, 0.2, ia - max(0, ia - R)))
    env[ib:min(N, ib + R)] = np.minimum(env[ib:min(N, ib + R)], np.linspace(0.2, 1, min(N, ib + R) - ib))
SW = EDG.load_words(CFG.get("words", "src_words.json"))
for w in WN:
    if w["kind"] != "A" or under(w["a"], w["b"]): continue
    L = (w["b"] - w["a"]) * SPD
    if any(w["s"] < x[1] - 0.1 and w["s"] + L > x[0] + 0.1 for x in SW): ia, ib = int(w["a"] * SR), int(w["b"] * SR); env[ia:ib] = np.minimum(env[ia:ib], 0.3)
for w in WN:
    L = (w["b"] - w["a"]) * w.get("rate", SPD if w["kind"] == "A" else 1.0); s0 = w["s"] - w.get("pre", 0)
    if any(s0 < b and s0 + L > a for a, b in CFG.get("quiet", [])): ia, ib = int(w["a"] * SR), int(w["b"] * SR); env[ia:ib] *= CFG.get("quiet_gain", 0.35)
org *= env[:, None]
nar = np.zeros((N, 2), np.float32)
for _, t, d, p in narr:
    x = load(p); k = int(t * SR); nar[k:k + len(x)] += x[:N - k]
save("narr_track.wav", nar); save("mix.wav", org + nar)
r = subprocess.run([sys.executable, os.path.join(HERE, "..", "v9", "gate.py"), "final", "subs_shorts.ass", "narr_track.wav"], text=True, encoding="utf-8", errors="replace")
if r.returncode: sys.exit("관문 final 에 걸림 — 굽지 않는다")

# ── 굽기
fc = (f"[0:v]crop={CW}:1080:x='{xe}':y=0,scale={W}:{MH},unsharp=5:5:0.85:5:5:0,tpad=stop_mode=clone:stop_duration={END - BODY + 0.05:.2f},"
      f"pad={W}:{H}:0:{MY0}:black[v0];[v0][2:v]overlay=0:0[v1];[v1]subtitles=subs_shorts.ass:fontsdir=fonts_shorts,format=yuv420p[v];"
      f"[1:a]atrim=0:{END:.3f},afade=t=out:st={END - 0.15:.3f}:d=0.15,alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
open("fc_shorts.txt", "w", encoding="utf-8").write(fc)
out = "shorts.mp4"
subprocess.run(FF + ["-i", "body.mkv", "-i", "mix.wav", "-i", "_frame.png", "-/filter_complex", "fc_shorts.txt", "-map", "[v]", "-map", "[a]", "-t", f"{END:.3f}",
                     "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out + ".tmp.mp4"], check=True)
os.replace(out + ".tmp.mp4", out)
def lufs(p):
    o = subprocess.run(["ffmpeg", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]), max(float(x) for x in re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o)[-2:])
Il, TP = lufs(out)
for lim in (0.8, 0.7):                    # build_v9 「소리 맞춤」과 같이: 영상 복사 + 소리만
    if abs(Il + 16) <= 0.3 and TP <= -1.0: break
    subprocess.run(FF + ["-i", out, "-c:v", "copy", "-af", f"aresample=192000,volume={-16 - Il:.2f}dB,alimiter=limit={lim}:level=disabled:attack=1:release=60,aresample=48000",
                         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "_lv.mp4"], check=True)
    os.replace("_lv.mp4", out); Il, TP = lufs(out)
o = subprocess.run(["ffmpeg", "-t", "1", "-i", out, "-vn", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
print("쇼츠", round(dur(out), 2), "초 ·", Il, "LUFS · 정점", TP, "· 0~1초 소리", re.findall(r"mean_volume: (-?[\d.]+)", o))
# 확인용 시트(3초마다)
n = int(dur(out) // 3)
subprocess.run(FF + ["-i", out, "-vf", f"fps=1/3,scale=270:480,tile=10x{(n + 10) // 10}", "-frames:v", "1", "_시트.jpg"], check=True)
dst = os.path.join(FINAL, NAME + ".mp4"); shutil.copy2(out, dst); print("→", dst)
