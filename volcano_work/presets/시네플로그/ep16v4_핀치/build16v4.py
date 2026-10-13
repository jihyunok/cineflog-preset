# -*- coding: utf-8 -*-
"""시네플로그 16 핀치 v4 (2026-10-12) — 강의 규칙(docs/영화리뷰_공부/2주차_1부_정리.md) 그대로
- 나레 26조각 뺌(장면·대사가 설명하는 것). ni 번호는 유지(narr/nNNN).
- 줄거리(ni 5~103) 나레 사이 원본 구간은 "C" 사슬: 자막 있는 대사는 말 끝까지(3초 넘으면 반전, ≤3.95),
  말 없는 곳은 장면 전환 기준 2.9초 액션 컷, 쓰면 3초 이상 건너뜀. 나레가 꼭 오지 않아도 된다.
- 목표: 나레 약 33%, 완성 약 25분(원본 107분의 25% 안).
- 자막 키움(10-12 "글자크기 좀더 키워줘"): N 100 · D 104. mp4 에 4K 필터 비슷한 선명(unsharp). 캡컷은 capcut_style04(4K 0.50).
사용: python build16v4.py plan → items.json + 숫자 · prep → 대사/원본 컷 · (없음) → 굽기"""
import json, math, os, re, subprocess, sys, importlib, wave
FF = ["ffmpeg", "-v", "error", "-y"]
SRC = "src.mp4"; SPEED = 1.05; MAXC = 2.9; GAP = 3.0; EXT = 25.0; END = 6440.0
W, H, BAR = 1920, 1080, 138
EQ = "eq=saturation=1.12:contrast=1.04:brightness=0.01,hue=h=4"
VF_BASE = "crop=1830:766:45:19,scale=1920:804," + EQ
VF_ZOOM = "crop=1352:566:284:2,scale=1920:804," + EQ
EVL = json.load(open("subev.json")); EV = {e["id"]: e for e in EVL}
SUBEV = [(e["s"] - 0.25, e["e"] + 0.25) for e in EVL]
KO = json.load(open("ko16.json", encoding="utf-8"))
DEND = json.load(open("dend.json")) if os.path.exists("dend.json") else {}
BAN = [(0, 62)]
DROP = {10, 11, 12, 14, 19, 20, 23, 28, 29, 32, 39, 43, 45, 46, 49, 56, 57, 60, 65, 71, 73, 76, 86, 89, 90, 92}
PLOT = (5, 103)
ORIG_TARGET = float(os.environ.get("ORIG_TARGET", 1000))
MODE = sys.argv[1] if len(sys.argv) > 1 else "build"
os.makedirs("clips", exist_ok=True); os.makedirs("blocks", exist_ok=True)
cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", open("scenes.txt").read())]

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
def wdur(p):
    w = wave.open(p); return w.getnframes() / w.getframerate()
def dlen(eid):
    e = EV[eid]; ln = round(e["e"] - e["s"] + 0.2, 2)
    if str(eid) in DEND and DEND[str(eid)]: ln = min(ln, round(DEND[str(eid)] - e["s"] + 0.35, 2))
    return ln

used = []
def free(s, e):
    return all(e + GAP <= a or s >= b + GAP for a, b in used) and all(e <= a or s >= b for a, b in BAN)
def ditem(eid, maxlen):
    ln = dlen(eid)
    if 5.9 < ln <= 6.3: ln = 5.9
    if ln > maxlen: return None
    s = round(EV[eid]["s"] - 0.05, 3)
    return {"type": "D", "i": eid, "s": s, "d": max(ln, 1.0), "ko": KO[str(eid)], "mirror": ln > 2.95}

def pick(a, b, n, ls):
    out = []; x = a; hi = min(b + EXT, END)
    while len(out) < n:
        if out: x = max(x, out[-1][1] + GAP)
        cand = [c + 0.1 for c in cuts if x <= c + 0.1 <= x + 1.0]
        got = None
        for s in cand + [x + k * 0.25 for k in range(int((hi - x) / 0.25) + 1)]:
            if s + ls > hi: break
            if free(s, s + ls): got = s; break
        if got is None: break
        out.append((got, got + ls)); used.append((got, got + ls)); x = got + ls
    return out, n - len(out)

def chain(lo, hi, target):
    """[lo,hi] 에서 원본 사슬. 대사(자막 있는 것)는 말 끝까지, 아니면 2.9초 액션. 쓴 뒤 3초 이상 건너뜀."""
    out = []; got = 0.0; x = lo
    span = max(hi - lo, 1); stride = max(2.9 + GAP, span / max(target / 2.9, 1))
    while x < hi - 2.0 and got < target:
        s0 = x; took = None
        evs = [e for e in EVL if x <= e["s"] - 0.05 <= x + 1.5 and KO.get(str(e["id"]), "X") != "X"]
        for e in evs:
            q = ditem(e["id"], 3.95)
            if q and q["s"] + q["d"] <= hi and free(q["s"], q["s"] + q["d"]): took = q; break
        if not took:
            for s in [c + 0.1 for c in cuts if x <= c + 0.1 <= x + 1.0] + [x]:
                e = s + MAXC
                if e <= hi and free(s, e) and not any(s < b and e > a for a, b in SUBEV):
                    took = {"type": "D", "i": 0, "s": round(s, 3), "d": MAXC, "ko": "", "mirror": False}; break
        if took:
            out.append(took); used.append((took["s"], took["s"] + took["d"])); got += took["d"]
            x = max(took["s"] + took["d"] + GAP, s0 + stride)
        else:
            x += 0.5
    return out, got

if MODE == "plan":
    EP = importlib.import_module("ep16v3")
    seq = []; ni = 0
    for x in EP.S:
        if x[0] == "N":
            ni += 1; seq.append({"type": "N", "ni": ni, "text": x[1], "rng": [x[2], x[3]]})
        else:
            q = ditem(x[1], 5.9) if KO.get(str(x[1]), "X") != "X" else None
            if q: seq.append(q)
    seq = [q for q in seq if not (q["type"] == "N" and q["ni"] in DROP)]
    for q in seq:
        if q["type"] == "D": used.append((q["s"], q["s"] + q["d"]))
    nsec = 0
    for q in seq:      # 나레 화면 먼저
        if q["type"] != "N": continue
        nd = wdur(f"narr/n{q['ni']:03d}.wav"); total = nd + 0.12; nsec += total
        n = max(1, math.ceil(total / (MAXC / SPEED))); lo = total / n; ls = lo * SPEED
        pk, miss = pick(q["rng"][0], q["rng"][1], n, ls)
        q.update({"picks": pk, "lo": lo, "ls": ls, "miss": miss})
    fixed = sum(q["d"] for q in seq if q["type"] == "D")
    NI = [k for k, q in enumerate(seq) if q["type"] == "N" and PLOT[0] <= q["ni"] <= PLOT[1]]
    gaps = []
    for k1, k2 in zip(NI, NI[1:]):
        a = seq[k1]; b = seq[k2]
        lo = max([p[1] for p in a["picks"]] + [a["rng"][0]]) + GAP; hi = min([p[0] for p in b["picks"]] + [b["rng"][1]]) - GAP
        if hi - lo > 6: gaps.append((k1, k2, lo, hi))
    tot = sum(h - l for _, _, l, h in gaps); budget = max(0, ORIG_TARGET - fixed)
    ins = {}; csec = 0
    for k1, k2, lo, hi in gaps:
        c, g = chain(lo, hi, budget * (hi - lo) / tot); ins[k2] = c; csec += g
    items = []
    for k, q in enumerate(seq):
        if k in ins:     # 앞 나레 뒤 고정 대사와 사슬을 시간순으로 합친다
            j = len(items)
            while j > 0 and items[j - 1]["type"] == "D": j -= 1
            items = items[:j] + sorted(items[j:] + ins[k], key=lambda z: z["s"])
        items.append(q)
    json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    D = [q for q in items if q["type"] == "D"]; osec = sum(q["d"] for q in D)
    allsp = sorted([(q["s"], q["s"] + q["d"]) for q in D] + [tuple(p) for q in items if q["type"] == "N" for p in q["picks"]])
    close = sum(1 for i in range(len(allsp) - 1) if allsp[i + 1][0] - allsp[i][1] < GAP - 0.01)
    npk = sum(p[1] - p[0] for q in items if q["type"] == "N" for p in q["picks"])
    print(f"나레 {sum(q['type']=='N' for q in items)}조각 {nsec:.0f}초 · 고정대사 {fixed:.0f}초 · 사슬 {csec:.0f}초({sum(len(v) for v in ins.values())}컷, 대사 {sum(1 for v in ins.values() for z in v if z['ko'])})")
    print(f"원본소리구간 {osec:.0f}초 · 완성 약 {(nsec+osec)/60:.1f}분 · 나레 {100*nsec/(nsec+osec):.0f}% · 원본 사용 {(osec+npk)/60:.1f}분 · 간격3초미만 {close}")
    for q in items:
        if q["type"] == "N" and q["miss"]: print(f" ! n{q['ni']:03d} 컷 모자람 {q['miss']} {q['rng']} 「{q['text'][:20]}」")
    sys.exit()

IT = json.load(open("items.json", encoding="utf-8"))
def yellow(s, e): return any(s < y and e > x for x, y in SUBEV)
def clip(path, s, ls, speed, mirror, gain_db, lo):
    if os.path.exists(path): return
    vf = (VF_ZOOM if yellow(s, s + ls) else VF_BASE) + (",hflip" if mirror else "") + f",pad={W}:{H}:0:{BAR}:black,setpts=PTS/{speed},fps=30,format=yuv420p"
    af = (f"atempo={speed}," if speed != 1 else "") + f"volume={gain_db}dB" + (",alimiter=limit=0.9" if gain_db > 0 else "") + ",aresample=48000"
    subprocess.run(FF + ["-ss", f"{s:.3f}", "-t", f"{ls:.3f}", "-i", SRC, "-vf", vf, "-af", af, "-t", f"{lo:.3f}",
                         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "pcm_s16le", "-ac", "2", path], check=True)
segs = []
def dclip(q):
    tag = f"d{int(q['s']*100):07d}"; p = f"blocks/{tag}.mkv"
    clip(p, q["s"], q["d"], 1, q["mirror"], 17.5 if q["ko"] else 6, q["d"])
    segs.append(("D", p, {"ko": q["ko"]}))
def nseg(q):
    tag = f"n{q['ni']:03d}"; nw = f"narr/{tag}.wav"; cl = []
    if q["miss"]: sys.exit(f"컷 모자람 {tag}")
    for k, (s0, e0) in enumerate(q["picks"]):
        p = f"clips/{tag}_{k}.mkv"; clip(p, s0, q["ls"], SPEED, False, -13, q["lo"]); cl.append(p)
    out = f"blocks/{tag}.mkv"
    if not os.path.exists(out):
        lst = f"blocks/{tag}.txt"; open(lst, "w").write("".join(f"file '../{c}'\n" for c in cl))
        subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", lst, "-i", nw, "-filter_complex",
                             "[1:a]adelay=60|60,apad[n];[0:a][n]amix=inputs=2:normalize=0:duration=first[a]",
                             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "pcm_s16le", out], check=True)
    segs.append(("N", out, {"json": f"narr/{tag}.json"}))

if MODE == "prep":
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as ex: list(ex.map(dclip, [q for q in IT if q["type"] == "D"]))
    print("대사·원본 컷", len(segs)); sys.exit()

for q in IT: (nseg if q["type"] == "N" else dclip)(q)

def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"
from PIL import ImageFont
NS, DS = 100, 104
FN = ImageFont.truetype("fonts/GyeonggiTitleB.ttf", NS); FD = ImageFont.truetype("fonts/Stylish.ttf", DS)
MAXW = 1300
def wid(t, f): return f.getlength(t)
def balance(s, f):
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
        al = json.load(open(m["json"], encoding="utf-8")); cs = chunks("".join(al["chars"]), al["st"], al["en"])
        for k, (s, a, b) in enumerate(cs):
            a2 = t0 + 0.06 + a; b2 = t0 + 0.06 + (cs[k + 1][1] if k + 1 < len(cs) else b + 0.25)
            ev.append(("N", a2, min(b2, t0 + L), s))
    elif m["ko"]:
        ps = balance(m["ko"], FD); a0 = t0 + 0.05; span = L - 0.07; tot = sum(len(x) for x in ps)
        for x in ps:
            d0 = span * len(x) / tot; ev.append(("D", a0, a0 + d0, x)); a0 += d0
    t0 += L
BODY = t0
ev = [(k, a, max(b, a + 0.3), s) for k, a, b, s in ev]
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: N,GyeonggiTitle,{NS},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,-1,0,0,100,100,0,0,1,5,1,2,60,60,90,1
Style: D,Stylish,{DS},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,-1,0,0,100,100,0,0,1,5,1,2,60,60,90,1
Style: TOP,Noto Sans KR Black,104,&H00B5B5B5,&H00B5B5B5,&H00000000,&H64000000,-1,-1,0,0,100,100,0,0,1,4,0,9,40,40,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0)},{ts(BODY)},TOP,,0,0,0,,CINEFLOG
"""
for k, a, b, s in ev: ass += f"Dialogue: 0,{ts(a)},{ts(b)},{k},,0,0,0,,{s}\n"
open("subs.ass", "w", encoding="utf-8").write(ass)
open("all.txt", "w").write("".join(f"file '{p}'\n" for _, p, _ in segs))
subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", "all.txt", "-c", "copy", "body.mkv"], check=True)
nlast = [i for i, s in enumerate(segs) if s[0] == "N"][-4]
t_out = sum(dur(p) for _, p, _ in segs[:nlast]); OUT = 18
music = os.path.expanduser(r"~/volcano_work/달빛롱폼/bgm/") + "Healing.mp3"
mus = f"music_{os.getpid()}.mp3"; subprocess.run(FF + ["-i", music, "-t", str(BODY - t_out + OUT), "-c", "copy", mus], check=True)
fc = (f"[0:v]unsharp=5:5:0.55:5:5:0,tpad=stop_mode=add:stop_duration={OUT}:color=black,subtitles=subs.ass:fontsdir=fonts[v];"
      f"[0:a]apad=pad_dur={OUT}[b];"
      f"[1:a]aresample=48000,volume='if(lt(t,{BODY - t_out:.2f}),0.10,0.5)':eval=frame,afade=t=in:d=2,afade=t=out:st={BODY - t_out + OUT - 3:.2f}:d=3,adelay={int(t_out*1000)}|{int(t_out*1000)}[m];"
      f"[b][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
subprocess.run(FF + ["-i", "body.mkv", "-i", mus, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "final.mp4"], check=True)
os.remove(mus)
print("final", round(dur("final.mp4") / 60, 2), "분")
