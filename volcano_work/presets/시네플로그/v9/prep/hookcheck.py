# -*- coding: utf-8 -*-
"""★11-07 훅 첫 10초 사람 확인 시트 — 화면 0~10초를 0.5초마다 원본에서 뽑아(완성본처럼 반전) hook_sheet.jpg(5칸), 아래에 그 10초에 나오는 나레·대사.
(33 콜래트럴: 훅 0:00 「택시 위로 남자가 떨어집니다」 밑에 택시도 추락도 안 나옴 — 글 판정만 믿고 아무도 프레임을 안 봄)
hook_check.json 은 없거나 앞 10초 조각 서명(v9/hooksig.py)이 바뀌었을 때만 새로 쓴다(옛것은 hook_check_old.json). 사람이 시트를 보고 채우면 gate ⑯ 이 확인한다.
사용: python hookcheck.py   (작업 폴더: ep.json · windows.json · narr_place.json · script.py · narr/nNNN.json 있으면 문장 시각)"""
import json, os, re, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import hooksig as HS
CFG = json.load(open("ep.json", encoding="utf-8")); SRC = CFG["src"]
W = json.load(open("windows.json", encoding="utf-8")); PL = json.load(open("narr_place.json", encoding="utf-8"))
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
N = [x[1] for x in ns["S"] if x[0] == "N"]
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
def rate(w): return w.get("rate", 1.05 if w["kind"] == "A" else 1.0)
def s0(w): return w["s"] - w.get("pre", 0)
END = HS.HOOK_SEC
HW = HS.hook_windows(W); JX = {id(w): j for j, w in enumerate(W)}
# 나레 문장(화면 시각) — narr/nNNN.json 글자 시각이 있으면 문장마다, 없으면 줄 통째
SENT = []
for q in sorted(PL, key=lambda q: q["t"]):
    if q["t"] >= END: continue
    n = q["ni"]; text = N[n - 1] if n - 1 < len(N) else ""; p = f"narr/n{n:03d}.json"
    j = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    text = j.get("text", text); ch, st, en = j.get("chars"), j.get("st"), j.get("en") or j.get("st")
    if ch and st and len(st) == len(ch) == len(en) and "".join(ch) == text:
        i0 = 0
        for m in list(re.finditer(r"[.?!…]+(\s+|$)", text)) + [None]:
            i1 = m.end() if m else len(text)
            idx = [i for i in range(i0, i1) if not text[i].isspace()]
            if idx:
                t0, t1 = q["t"] + st[idx[0]], q["t"] + en[idx[-1]]
                if t0 < END: SENT.append((t0, t1, n, text[idx[0]:idx[-1] + 1]))
            i0 = i1
            if i1 >= len(text): break
    else: SENT.append((q["t"], q["t"] + q.get("d", 0), n, text))
DLG = []                                                  # 대사 창 자막(원본 초 기준 → 화면 초)
for w in HW:
    if w["kind"] == "D":
        for t, r0, r1 in w.get("subs") or ([[w.get("ko", ""), 0, (w["b"] - w["a"]) * rate(w)]] if w.get("ko") else []):
            a = w["a"] + r0 / rate(w)
            if a < END: DLG.append((a, w["a"] + r1 / rate(w), t))
def spoken(t):
    s = [x for x in SENT if x[0] - 0.05 <= t < x[1] + 0.05]
    if s: return "나레: " + s[0][3]
    d = [x for x in DLG if x[0] - 0.05 <= t < x[1] + 0.05]
    return ("대사: " + d[0][2]) if d else ""
# 0.5초마다 프레임
T = []
t = 0.0
while t < min(END, W[-1]["b"]) - 1e-6:
    w = next((w for w in W if w["a"] - 1e-6 <= t < w["b"]), None)
    if w: T.append((t, w, s0(w) + (t - w["a"]) * rate(w), not w.get("noflip")))
    t = round(t + 0.5, 3)
os.makedirs("_hook", exist_ok=True)
def grab(x):
    t, w, s, flip = x; p = f"_hook/{max(s, 0):.2f}_{int(flip)}.jpg"
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(s, 0):.3f}", "-i", SRC, "-frames:v", "1", "-vf", ("hflip," if flip else "") + "scale=384:-2", "-q:v", "3", p + ".tmp.jpg"])
        if os.path.exists(p + ".tmp.jpg"): os.replace(p + ".tmp.jpg", p)
    return p if os.path.exists(p) else None
with ThreadPoolExecutor(8) as ex: FR = list(ex.map(grab, T))
if not any(FR): sys.exit("프레임을 하나도 못 뽑음 — ep.json src 확인")
FD = CFG.get("fonts", "fonts"); FP = f"{FD}/Cafe24Dangdanghae.ttf" if os.path.exists(f"{FD}/Cafe24Dangdanghae.ttf") else r"C:\Windows\Fonts\malgun.ttf"
F1, F2, F3 = (ImageFont.truetype(FP, z) for z in (16, 15, 22))
def fit(s, f, wmax):
    while s and f.getlength(s) > wmax: s = s[:-1]
    return s
C, CW = 5, 384; FH = next(Image.open(p).size[1] for p in FR if p); LH = 44; TH = LH + FH + 4
lines = [f"{mm(a)}~{mm(b)}  나레 n{n:03d} | {s}" for a, b, n, s in SENT] + [f"{mm(a)}~{mm(b)}  대사 | {s}" for a, b, s in DLG]   # 「」 는 당당해 글꼴에 없음
lines = [x for _, x in sorted(zip([a for a, *_ in SENT] + [a for a, *_ in DLG], lines))] or ["(앞 10초 나레·대사 없음)"]
rows = (len(T) + C - 1) // C; BH = 40 + 30 * len(lines)
im = Image.new("RGB", (C * CW, rows * TH + BH), (16, 16, 16)); d = ImageDraw.Draw(im)
COL = [(255, 220, 0), (120, 220, 255)]
for i, ((t, w, s, flip), p) in enumerate(zip(T, FR)):
    x0, y0 = (i % C) * CW, (i // C) * TH; j = JX[id(w)]; c = COL[HW.index(w) % 2] if w in HW else (200, 200, 200)
    d.text((x0 + 4, y0 + 2), fit(f"화면 {t:4.1f}초 · 원본 {mm(s)} · w{j} {w['kind']}" + ("" if flip else " 반전X"), F1, CW - 8), font=F1, fill=c)
    d.text((x0 + 4, y0 + 22), fit(spoken(t), F2, CW - 8), font=F2, fill=(255, 255, 255))
    if p: im.paste(Image.open(p).convert("RGB").resize((CW, FH)), (x0, y0 + LH))
    else: d.text((x0 + 10, y0 + LH + 10), "프레임 못 뽑음", font=F1, fill=(255, 80, 80))
    d.rectangle([x0, y0 + LH, x0 + CW - 1, y0 + LH + FH - 1], outline=c, width=2)
y = rows * TH + 8; d.text((8, y), "앞 10초에 나오는 말 (조각 색이 바뀌면 다른 조각)", font=F3, fill=(255, 220, 0)); y += 32
for ln in lines: d.text((8, y), fit(ln, F3, C * CW - 16), font=F3, fill=(255, 255, 255)); y += 30
im.save("hook_sheet.jpg", quality=88)
NARR = " ".join(s for *_, s in SENT)
print(f"hook_sheet.jpg — 프레임 {len(T)}장 · 앞 10초 조각 {len(HW)}개 · 못 뽑은 프레임 {sum(1 for p in FR if not p)}")
for ln in lines: print("  ", ln)
SIG = HS.sig(W); HP = "hook_check.json"
old = json.load(open(HP, encoding="utf-8")) if os.path.exists(HP) else None
if old is not None and old.get("win_sig") == SIG: print(f"{HP} 그대로(앞 10초 조각 안 바뀜) — 채운 것 유지")
else:
    if old is not None: shutil.copy(HP, "hook_check_old.json"); print(f"앞 10초 조각이 바뀜 → 옛 확인은 hook_check_old.json 으로 · 다시 보고 채울 것")
    json.dump({"win_sig": SIG, "sheet": "hook_sheet.jpg", "narration": NARR, "key_scene": "", "key_scene_shown": None,
               "pieces": [{"w": JX[id(w)], "kind": w["kind"], "a": w["a"], "b": w["b"], "s": w["s"], "seen": "", "ok": None} for w in HW]},
              open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{HP} 새로 씀 (조각 {len(HW)}개)")
print("할 일(사람이 눈으로 — 안 보고 채우지 말 것):\n"
      "  1) hook_sheet.jpg 를 연다(0.5초마다 · 칸 위 화면 초 · 원본 시각 · 조각 번호 · 그때 나오는 말).\n"
      "  2) hook_check.json pieces 마다 seen 에 그 조각 프레임에 실제로 보이는 것(인물·장소·물건·행동, 8자+, 조각마다 다르게)을 적고,\n"
      "     나레·대사와 맞으면 ok true, 아니면 false.\n"
      "  3) key_scene 에 나레가 말한 장면(예: 「택시 위로 남자가 떨어짐」)을 적고, 그 장면이 시트에 실제로 나올 때만 key_scene_shown true.\n"
      "  4) 안 맞으면 대본·plan 을 고친 뒤 hookcheck.py 다시. 못 봤으면 비워 둔다 — gate ⑯ 이 막는다.")
