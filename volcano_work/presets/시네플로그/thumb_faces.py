# -*- coding: utf-8 -*-
"""11-08 썸네일 = 남주·여주 얼굴 (사용자 「남주 여주 인물 위주로」「장면 없어도 돼」「인물은 됬는데 텍스트를 좀 바꿔. 최근 떡상한 영화보고 바꿔」 「다른 썸네일도 바꿔」)
1) cand  : python thumb_faces.py cand "G:/내 드라이브/영화/NN_제목" [이름1 이름2]
   → 수정용 작업 폴더의 shots.json 에서 가장 많이 나온 두 인물(또는 준 이름)의 「혼자 나온」 컷(ep.json avoid·피·싸움 낱말 밖)
     → <G폴더>/수정용/_th_faces/fr/<초>.jpg + sheet_<이름>_N.jpg(초 번호 붙은 접촉 시트) · cand.json
2) 고르기: 시트를 눈으로 보고 정면·선명·피/상처/멍 없는 얼굴, 민감 장면(성추행·자해 회상 등) 아닌 컷 · 얼굴 가운데 x(1920 기준) 적기
3) make  : python thumb_faces.py make "G:/…/NN_제목" spec.json
   spec = {"items":[{"duo":[[초A,cxA],[초B,cxB]] 또는 "one":[초,cx], "white":"…","red":"…","labels":["0.25,0.03,g,(별명)",…]}, … 5개]}
   → 옛 썸네일보기를 수정용/옛썸네일 로 옮기고 NN_제목_썸네일보기_1..5 + _한눈에 새로
글자: thumb_label.py(아래 = 인물 대사·반응처럼 짧게 흰+빨강, 머리 위 괄호 별명표 초록 g·노랑 y). 「죽여」「뒤져」「사살」 등 금지."""
import os, sys, json, re, glob, subprocess, collections, shutil
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
BAD = r'blood|bleed|wound|injur|dead|body|corpse|gun to|shoot|shot by|fight|strangl|chok|tackl|wrestl|grappl|punch|kick|stab|knife|kill|naked|shirtless|underwear|kiss|bed|sex|cry|tear'
F = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)

def paths(g):
    fix = os.path.join(g, "수정용")
    src = [p for p in glob.glob(os.path.join(fix, "원본", "**", "*"), recursive=True) if p.lower().endswith((".mkv", ".mp4", ".avi", ".mov", ".m4v", ".ts"))]
    src = max(src, key=os.path.getsize) if src else None
    work = [d for d in glob.glob(os.path.join(fix, "ep*")) if os.path.isdir(d)]
    work = work[0] if work else None
    return fix, src, work

def probe_h(src):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True, encoding="utf-8", errors="replace")
    w, h = [int(x) for x in r.stdout.strip().split(",")[:2]]
    return round(h * 1920 / w)          # 1920 폭으로 맞춘 높이

def cropdetect(src, H):
    """검은 띠 위·아래(1920 폭 기준) — 영화 가운데 5곳에서 cropdetect."""
    ys = []
    for frac in (0.2, 0.35, 0.5, 0.65, 0.8):
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True, encoding="utf-8", errors="replace")
        t = float(r.stdout.strip() or 3600) * frac
        r = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(t), "-i", src, "-frames:v", "12", "-vf", "scale=1920:-2,cropdetect=24:2:0", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        m = re.findall(r"crop=\d+:(\d+):\d+:(\d+)", r.stderr)
        if m: ys.append((int(m[-1][1]), int(m[-1][1]) + int(m[-1][0])))
    if not ys: return 0, H
    return min(y for y, _ in ys), max(z for _, z in ys)

def band(work, src=None):
    """그림 띠(1920 폭 기준 y0,y1)와 avoid. ★11-08: fill_box 가 원본 높이와 안 맞거나(작업 파일 기준) 없으면 cropdetect.
    박힌 자막이 그림 안 아래에 있으면 ep.json "thumb_y1"(1920 폭 기준)로 자막 윗줄까지만."""
    try: ep = json.load(open(os.path.join(work, "ep.json"), encoding="utf-8"))
    except Exception: ep = {}
    av = ep.get("avoid", [])
    H = probe_h(src) if src else 1080
    if ep.get("thumb_band"): y0, y1 = ep["thumb_band"]; return y0, y1, av
    fb = ep.get("fill_box")
    if fb and fb[3] <= H and H == 1080 and fb[1] > 0: y0, y1 = fb[1], fb[3]
    else: y0, y1 = cropdetect(src, H) if src else (0, H)
    if ep.get("thumb_y1"): y1 = min(y1, ep["thumb_y1"])
    return y0, y1, av

def grab(src, t, y0, y1, out):
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", src, "-frames:v", "1",
                        "-vf", f"scale=1920:-2,crop=1920:{y1-y0}:0:{y0}", "-q:v", "2", out])
    return out

def cand(g, names=None):
    fix, src, work = paths(g); assert src and work, ("원본/작업 폴더 없음", src, work)
    d = json.load(open(os.path.join(work, "shots.json"), encoding="utf-8"))
    y0, y1, av = band(work, src)
    c = collections.Counter()
    for x in d:
        for m in set(re.findall(r'([A-Z][\w\.\'\- ]+?) \(([A-Z][^)]+)\)', x["desc"])):
            n0 = m[0].strip()
            if re.match(r'(At|In|On|Inside|Outside|Near|Under|Over)\b', n0): continue   # 장소 이름 빼기(58 「At Camp Nathaniel」)
            c[n0] += 1
    names = names or [n for n, _ in c.most_common(2)]
    print("인물:", c.most_common(5), "→", names)
    out = os.path.join(fix, "_th_faces"); os.makedirs(os.path.join(out, "fr"), exist_ok=True)
    res = {"src": src, "y0": y0, "y1": y1, "names": {}}
    for n in names:
        ts = []
        for x in d:
            t, s, e = x["desc"], x["s"], x["e"]
            if n not in t or t.count("(") != 1 or e - s < 1.2 or re.search(BAD, t, re.I): continue
            if any(a < e + 1 and s - 1 < b for a, b in av): continue
            ts.append(round((s + e) / 2, 1))
        if len(ts) > 48: ts = [ts[round(i * (len(ts) - 1) / 47)] for i in range(48)]
        res["names"][n] = ts
        for si in range(0, len(ts), 24):
            part = ts[si:si + 24]; W, H = 400, int(400 * (y1 - y0) / 1920)
            sh = Image.new("RGB", (W * 4, H * 6)); dr = ImageDraw.Draw(sh)
            for i, t in enumerate(part):
                im = Image.open(grab(src, t, y0, y1, os.path.join(out, "fr", f"{t}.jpg"))).resize((W, H))
                sh.paste(im, ((i % 4) * W, (i // 4) * H))
                dr.text(((i % 4) * W + 4, (i // 4) * H + 2), str(t), font=F, fill="yellow", stroke_width=2, stroke_fill="black")
            p = os.path.join(out, f"sheet_{re.sub(r'[^A-Za-z]', '', n)}_{si // 24}.jpg"); sh.save(p, quality=85); print(p)
    json.dump(res, open(os.path.join(out, "cand.json"), "w", encoding="utf-8"), ensure_ascii=False)

def frame(g, t):
    fix, src, work = paths(g); y0, y1, _ = band(work, src)
    return Image.open(grab(src, t, y0, y1, os.path.join(fix, "_th_faces", "fr", f"{t}.jpg")))

def half(im, cx):
    h = im.height; w = round(h * 1020 / 1080); x0 = max(0, min(im.width - w, int(cx - w / 2)))
    return im.crop((x0, 0, x0 + w, h)).resize((1020, 1080), Image.LANCZOS)

def make(g, spec):
    fix, src, work = paths(g); out = os.path.join(fix, "_th_faces"); os.makedirs(out, exist_ok=True)
    sp = json.load(open(spec, encoding="utf-8"))
    base = os.path.basename(g.rstrip("/\\")); news = []
    sys.path.insert(0, HERE); from thumb_label import make as label
    for k, it in enumerate(sp["items"], 1):
        if "duo" in it:
            (ta, ca), (tb, cb) = it["duo"]
            L = half(frame(g, ta), ca); R = half(frame(g, tb), cb)
            can = Image.new("RGB", (1920, 1080)); can.paste(R, (900, 0))
            m = Image.new("L", (1020, 1080), 255); m.paste(Image.linear_gradient("L").rotate(-90, expand=True).resize((120, 1080)), (900, 0))
            can.paste(L, (0, 0), m); p = os.path.join(out, f"base{k}.jpg"); can.save(p, quality=95); x0, y0, hh = 0, 0, 0
        else:
            t, cx = it["one"]; im = frame(g, t); p = os.path.join(out, f"base{k}.jpg"); im.save(p, quality=95)
            hh = im.height; w = round(hh * 16 / 9); x0 = max(0, min(im.width - w, int(cx - w / 2))); y0 = 0
        o = os.path.join(out, f"new{k}.jpg"); label(p, x0, y0, hh, it.get("white", ""), it["red"], o, it.get("labels", [])); news.append(o)
    old = os.path.join(fix, "옛썸네일"); os.makedirs(old, exist_ok=True)
    if glob.glob(os.path.join(old, "*_썸네일보기_*.jpg")):          # ★다시 돌릴 때: 이미 옛 것이 있으면 지금 것(새 꼴 이전 판)은 _th_faces/prev 로
        old = os.path.join(out, "prev_%d" % len(glob.glob(os.path.join(out, "prev_*")))); os.makedirs(old, exist_ok=True)
    for f in glob.glob(os.path.join(g, "*_썸네일보기_*.jpg")): shutil.move(f, os.path.join(old, os.path.basename(f)))
    for k, o in enumerate(news, 1): shutil.copy(o, os.path.join(g, f"{base}_썸네일보기_{k}.jpg"))
    ims = [Image.open(o).resize((640, 360)) for o in news]
    s = Image.new("RGB", (1920, 720)); [s.paste(im, ((i % 3) * 640, (i // 3) * 360)) for i, im in enumerate(ims)]
    s.save(os.path.join(g, f"{base}_썸네일보기_한눈에.jpg"), quality=92); print("완료", g)

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "cand": cand(a[1], a[2:] or None)
    elif a[0] == "make": make(a[1], a[2])
