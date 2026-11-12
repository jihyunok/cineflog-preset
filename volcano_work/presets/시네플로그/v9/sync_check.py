# -*- coding: utf-8 -*-
"""시네플로그 완성본 재검사 — 11-07 33 콜래트럴 싱크 분석(D:/cine_work/분석_콜래트럴_싱크/scripts)을 한 도구로 묶은 것.
사용자 11-07 「너 왜이렇게만들었어?」 → 「틀린거 다 저장하고 박제해」 · 「다른영상들도 확인해」.

  python sync_check.py <작업 폴더> [--mp4 완성본.mp4] [--out 출력폴더] [--no-sheets] [--score 줄별_화면판정.csv]

작업 폴더에서 읽는 것: windows.json · narr_place.json · subs.ass(화면에 구운 자막) · narr_track.wav(있으면) · narr/nNNN.json(있으면)
숫자(출력폴더/sync_check.txt · .json):
 ① 결과 먼저: 나레 블록 밑 그림(A 조각) 가운데 가장 늦은 원본 시각보다 10초 넘게 앞선 원본을 쓰는 대사 창이
    그 블록 뒤(다음 나레 전)에 나오는 곳 — 창 수·초·블록 수, 블록마다 몇 초 앞섰나(큰 사건 = 10초+). 이어 붙은 조각끼리 10초+ 되감기 수.
 ② 나레↔대사 자막 겹침 · 나레가 대사 창(D) 위에 걸린 초.
 ③ 나레 소리↔자막: narr_track.wav 말소리 시작·끝과 블록 자막 시작·끝 차이.
 ④ 줄마다 초당 글자(띄어쓰기·문장부호 뺌).
 ⑤ 빈 곳: 나레도 대사 자막도 없는 3초+·5초+ 구간, 그중 완성본 소리도 −20dB 아래로 조용한 5초+ 구간(분석의 원음 −27dB 와 같은 곳).
 ⑥ 음량: 통합 LUFS·정점, 순간음량(400ms) 중앙값 나레 줄 vs 대사 줄 → 나레가 몇 LU 큰가(목표 2~3).
 ⑦ 훅 첫 10초 조각(원본 시각) — 사람이 프레임을 보고 나레가 말한 장면이 나오는지 적는다.
시트(출력폴더/sheets/): 나레 자막 줄마다 시작+0.1초·가운데 프레임(완성본에서) 8줄씩 한 장. 판정은 사람(세션)이 시트를 직접 보고
  줄별_화면판정.csv 의 verdict(O 맞음 / P 부분 / X 어긋남)·note 칸에 적는다(★보지 않은 줄은 비워 둔다 — 전역 규칙 11-07).
--score: 채운 csv 로 맞음·부분·어긋남 비율을 낸다(빈 칸이 있으면 「판정 안 한 줄」로 따로 센다)."""
import argparse, csv, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

ap = argparse.ArgumentParser()
ap.add_argument("work"); ap.add_argument("--mp4"); ap.add_argument("--out"); ap.add_argument("--no-sheets", action="store_true")
ap.add_argument("--score"); ap.add_argument("--ass")
A = ap.parse_args()
WK = os.path.abspath(A.work)
OUT = os.path.abspath(A.out or os.path.join(WK, "_sync")); os.makedirs(OUT, exist_ok=True)
def mmss(t): return f"{int(t // 60):02d}:{t % 60:04.1f}"

def score(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    tot = sum(float(r["dur"]) for r in rows); res = {}
    for v in ("O", "P", "X", ""):
        c = [r for r in rows if r["verdict"].strip().upper() == v]
        res[v or "빈칸"] = (len(c), 100 * len(c) / max(1, len(rows)), sum(float(r["dur"]) for r in c), 100 * sum(float(r["dur"]) for r in c) / max(1e-9, tot))
    names = {"O": "맞음", "P": "부분", "X": "어긋남", "빈칸": "판정 안 함"}
    out = [f"{names[k]} {n}줄 {p:.1f}% · {d:.1f}초 {dp:.1f}%" for k, (n, p, d, dp) in res.items()]
    bx = sorted({r["blk"] for r in rows if r["verdict"].strip().upper() == "X"}, key=lambda x: int(x or 0))
    out.append(f"어긋남 있는 블록 {len(bx)} {bx}")
    return out, res
if A.score:
    o, _ = score(A.score); print("\n".join(o)); sys.exit()

W = json.load(open(os.path.join(WK, "windows.json"), encoding="utf-8"))
PL = json.load(open(os.path.join(WK, "narr_place.json"), encoding="utf-8"))
MP4 = A.mp4 or os.path.join(WK, "final.mp4")
ASS = A.ass or os.path.join(WK, "subs.ass")
def tsec(x): h, m, s = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
narr, dia = [], []
for l in open(ASS, encoding="utf-8"):
    if not l.startswith("Dialogue"): continue
    f = l.rstrip("\n").split(",", 9); st = f[3]
    txt = re.sub(r"\{[^}]*\}", "", f[9]).replace("\\N", " ").strip()
    row = dict(s=tsec(f[1]), e=tsec(f[2]), text=txt)
    if st in ("N", "NP", "NE"): narr.append(row)
    elif st in ("D", "DJ", "DY"): dia.append(row)
narr.sort(key=lambda r: r["s"]); dia.sort(key=lambda r: r["s"])
for i, n in enumerate(narr):
    n["idx"] = i + 1; n["blk"] = None
    for p in PL:
        if p["t"] - 0.05 <= n["s"] <= p["t"] + p["d"] + 0.3: n["blk"] = p["ni"]
R = {"work": WK, "mp4": MP4}; T = []
def say(*a):
    s = " ".join(str(x) for x in a); T.append(s); print(s, flush=True)
END = W[-1]["b"]
say(f"# 재검사 {os.path.basename(WK)} — 완성본 {os.path.basename(MP4)} · 나레 블록 {len(PL)} · 나레 자막 {len(narr)}줄 · 대사 자막 {len(dia)}줄 · 조각 {len(W)}")

# ① 결과 먼저 · 되감기
def src_end(w): return w["s"] + (w["b"] - w["a"]) * w.get("rate", 1.05 if w["kind"] == "A" else 1.0)
ahead = []; cnt = 0; tot = 0.0
for i, p in enumerate(PL):
    a, b = p["t"], p["t"] + p["d"]; nxt = PL[i + 1]["t"] if i + 1 < len(PL) else 1e9
    As = [w for w in W if w["kind"] == "A" and w["b"] > a + 0.05 and w["a"] < b - 0.05 and w.get("z", "main") != "outro"]
    if not As: continue
    mx = max(w["s"] for w in As)
    worst = 0.0
    for w in W:
        if w["kind"] == "D" and b - 0.05 <= w["a"] < nxt and w.get("z", "main") != "outro" and w["s"] < mx - 10:
            cnt += 1; tot += w["b"] - w["a"]; worst = max(worst, mx - w["s"])
    if worst > 0:
        txt = " ".join(n["text"] for n in narr if n["blk"] == p["ni"])
        ahead.append(dict(ni=p["ni"], t=mmss(a), ahead=round(worst, 1), text=txt))
rew = []
for x, y in zip(W, W[1:]):
    if x.get("z", "main") != "main" or y.get("z", "main") != "main": continue
    if y["s"] < src_end(x) - 10: rew.append((round(y["a"], 2), round(src_end(x) - y["s"], 1), x["kind"], y["kind"]))
nD = sum(1 for w in W if w["kind"] == "D")
say(f"① 결과 먼저: 블록 {len(ahead)}/{len(PL)} · 대사 창 {cnt}/{nD}개 {tot:.1f}초 · 큰 사건(10초+ 앞섬) {len(ahead)}곳 · 20초+ {sum(1 for x in ahead if x['ahead'] >= 20)}곳")
for x in sorted(ahead, key=lambda x: -x["ahead"])[:15]: say(f"   B{x['ni']:02d} {x['t']} 그림이 뒤 대사보다 {x['ahead']}초 뒤 장면 | {x['text'][:60]}")
say(f"   이어 붙은 조각끼리 원본 10초+ 되감기 {len(rew)}번 (60초+ {sum(1 for r in rew if r[1] > 60)})")
R["result_first"] = dict(blocks=len(ahead), windows=cnt, sec=round(tot, 1), list=ahead, rewinds=len(rew), rewinds60=sum(1 for r in rew if r[1] > 60), rewind_list=rew)

# ② 겹침
ov = [(n["idx"], d["s"], round(min(n["e"], d["e"]) - max(n["s"], d["s"]), 3)) for n in narr for d in dia if min(n["e"], d["e"]) - max(n["s"], d["s"]) > 0.01]
onD = sum(max(0, min(n["e"], w["b"]) - max(n["s"], w["a"])) for n in narr for w in W if w["kind"] == "D")
say(f"② 나레↔대사 자막 겹침 {len(ov)}곳 {sum(o[2] for o in ov):.2f}초 · 나레가 대사 창 위 {onD:.2f}초")
R["overlap"] = dict(n=len(ov), sec=round(sum(o[2] for o in ov), 3), on_D=round(onD, 3), list=ov[:30])

# ③ 나레 소리 ↔ 자막 (narr_track.wav)
def load16(p):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.float32)
def env_db(x, hop=160):
    n = len(x) // hop; return 20 * np.log10(np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, 1) + 1e-12) + 1e-9)
NT = os.path.join(WK, "narr_track.wav")
if os.path.exists(NT):
    en = env_db(load16(NT)); sp = en > -50; res = []
    for i, p in enumerate(PL):
        ls = [n for n in narr if n["blk"] == p["ni"]]
        if not ls: continue
        s0, e0 = ls[0]["s"], ls[-1]["e"]
        lo = max(s0 - 0.5, (PL[i - 1]["t"] + PL[i - 1]["d"]) if i else 0); hi = min(e0 + 0.5, PL[i + 1]["t"] if i + 1 < len(PL) else len(sp) / 100)
        idx = np.where(sp[int(lo * 100):int(hi * 100)])[0]
        if len(idx): res.append((p["ni"], round(lo + idx[0] / 100 - s0, 2), round(lo + (idx[-1] + 1) / 100 - e0, 2)))
    on = np.array([r[1] for r in res]); off = np.array([r[2] for r in res])
    bad = [r for r in res if abs(r[1]) > 0.15 or abs(r[2]) > 0.25]
    say(f"③ 나레 소리↔자막: 블록 말 시작−자막 시작 중앙 {np.median(on):.2f}초(범위 {on.min():.2f}~{on.max():.2f}) · 말 끝−자막 끝 중앙 {np.median(off):.2f}초(범위 {off.min():.2f}~{off.max():.2f}) · 0.15/0.25초 넘는 블록 {len(bad)} {bad[:6]}")
    R["narr_sync"] = dict(onset_med=float(np.median(on)), onset_min=float(on.min()), onset_max=float(on.max()), off_med=float(np.median(off)), off_min=float(off.min()), off_max=float(off.max()), bad=bad)
else: say("③ narr_track.wav 없음 — 나레 소리↔자막 못 잼"); R["narr_sync"] = None

# ④ 초당 글자
PUN = set(" .,!?…·'\"“”‘’~-")
cps = sorted(((round(sum(1 for ch in n["text"] if ch not in PUN) / max(0.05, n["e"] - n["s"]), 2), n["idx"], mmss(n["s"]), n["text"]) for n in narr), reverse=True)
C = np.array([c[0] for c in cps]); du = np.array([n["e"] - n["s"] for n in narr])
say(f"④ 초당 글자: 중앙 {np.median(C):.2f} · 하위10% {np.percentile(C, 10):.2f} · 상위10% {np.percentile(C, 90):.2f} · 최대 {C.max():.2f} · 8 넘는 줄 {int((C > 8).sum())} · 줄 길이 중앙 {np.median(du):.2f}초 · 1초 안 되는 줄 {int((du < 1).sum())}")
R["cps"] = dict(median=float(np.median(C)), p10=float(np.percentile(C, 10)), p90=float(np.percentile(C, 90)), max=float(C.max()), over8=int((C > 8).sum()), top=cps[:8])

# ⑤ 빈 곳 · ⑥ 음량
FA = load16(MP4) if os.path.exists(MP4) else None
ef = env_db(FA) if FA is not None else None
def pw(e, a, b):
    seg = e[int(a * 100):int(b * 100)]; return 10 * np.log10(np.mean(10 ** (seg / 10)) + 1e-12) if len(seg) else -120
iv = sorted([(n["s"], n["e"]) for n in narr] + [(d["s"], d["e"]) for d in dia]); mg = []
for a, b in iv:
    if mg and a <= mg[-1][1] + 0.01: mg[-1][1] = max(mg[-1][1], b)
    else: mg.append([a, b])
gaps = []; prev = 0.0; fend = len(ef) / 100 if ef is not None else END
for a, b in mg + [[fend, fend]]:
    if a - prev >= 3.0: gaps.append((round(prev, 2), round(a, 2), round(a - prev, 2), round(pw(ef, prev, a), 1) if ef is not None else None))
    prev = max(prev, b)
quiet = [g for g in gaps if g[2] >= 5 and g[3] is not None and g[3] <= -20]   # 완성본 소리(16k 모노 RMS) −20dB ≈ 11-07 분석의 원음 트랙 −27dB(33편 10곳 + 1)
say(f"⑤ 빈 곳(나레·대사 자막 없음): 3초+ {len(gaps)}곳 {sum(g[2] for g in gaps):.1f}초 · 5초+ {sum(1 for g in gaps if g[2] >= 5)}곳 · 그중 소리도 조용(완성본 −20dB 아래) {len(quiet)}곳 {[(mmss(g[0]), g[2], g[3]) for g in quiet]}")
for g in sorted(gaps, key=lambda g: -g[2])[:6]: say(f"   {mmss(g[0])}–{mmss(g[1])} {g[2]}초 소리 {g[3]}dB")
R["gaps"] = dict(n3=len(gaps), sec3=round(sum(g[2] for g in gaps), 1), n5=sum(1 for g in gaps if g[2] >= 5), quiet5=quiet, list=gaps)
if os.path.exists(MP4):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-v", "verbose", "-i", MP4, "-vn", "-af", "ebur128=framelog=verbose:peak=true", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    M = [float(m.group(1)) if m.group(1) not in ("-inf", "nan") else -120 for m in re.finditer(r"t:\s*[\d.]+\s+TARGET.*?M:\s*(-?[\d.]+|-?inf|nan)\s+S:", o)]
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]); pk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o); TP = max(float(x) for x in pk[-2:]) if pk else None
    LRA = re.findall(r"LRA:\s+(-?[\d.]+) LU", o); M = np.array(M); tc = (np.arange(len(M)) + 1) / 10 - 0.2
    def mask(ivs):
        m = np.zeros(len(M), bool)
        for a, b in ivs: m |= (tc >= a + 0.2) & (tc <= b - 0.2)
        return m
    def med(m): v = M[m]; v = v[v > -70]; return float(np.median(v)) if len(v) else None
    mN, mDs = mask([(n["s"], n["e"]) for n in narr]), mask([(d["s"], d["e"]) for d in dia])
    nm, dm = med(mN), med(mDs)
    say(f"⑥ 음량: 통합 {I:.1f} LUFS · 정점 {TP} dBFS · LRA {LRA[-1] if LRA else '?'} · 순간음량 중앙 나레 {nm:.1f} / 대사 {dm:.1f} → 나레가 {nm - dm:.1f} LU 큼(목표 2~3)")
    R["loud"] = dict(I=I, TP=TP, LRA=float(LRA[-1]) if LRA else None, narr_M=nm, dlg_M=dm, diff=round(nm - dm, 1))
else: say("⑥ 완성본 없음 — 음량 못 잼"); R["loud"] = None

# ⑦ 훅 첫 10초
hk = [w for w in W if w["a"] < 10.0]
say("⑦ 훅 첫 10초 조각(화면초 → 원본초): " + " · ".join(f"{w['a']:.1f}→{mmss(w['s'])}{'' if w.get('noflip') else '(반전)'}" for w in hk))
say("   나레: " + " / ".join(n["text"] for n in narr if n["s"] < 10.0))
R["hook"] = [dict(a=w["a"], b=w["b"], s=w["s"], kind=w["kind"]) for w in hk]

# 시트 + csv 틀
def win_at(t): return next((w for w in W if w["a"] <= t < w["b"]), None)
for n in narr:
    n["t1"], n["t2"] = n["s"] + 0.1, (n["s"] + n["e"]) / 2
    for k in ("1", "2"):
        w = win_at(n["t" + k]); n["src" + k] = (w["s"] + (n["t" + k] - w["a"]) * w.get("rate", 1.05 if w["kind"] == "A" else 1.0)) if w else None
json.dump(narr, open(os.path.join(OUT, "narr_map.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
CSV = os.path.join(OUT, "줄별_화면판정.csv")
fresh = not os.path.exists(CSV)
with open(CSV if fresh else os.path.join(OUT, "줄별_화면판정_빈틀.csv"), "w", encoding="utf-8-sig", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=["idx", "blk", "start", "end", "dur", "src1", "src2", "text", "verdict", "note"]); wr.writeheader()
    for n in narr: wr.writerow(dict(idx=n["idx"], blk=n["blk"], start=mmss(n["s"]), end=mmss(n["e"]), dur=round(n["e"] - n["s"], 2), src1=mmss(n["src1"]) if n["src1"] is not None else "", src2=mmss(n["src2"]) if n["src2"] is not None else "", text=n["text"], verdict="", note=""))
say(f"판정 틀: {CSV if fresh else '(이미 있음 — 빈 틀은 줄별_화면판정_빈틀.csv)'}")
if not A.no_sheets and os.path.exists(MP4):
    from PIL import Image, ImageDraw, ImageFont
    FD = os.path.join(OUT, "frames"); SD = os.path.join(OUT, "sheets"); os.makedirs(FD, exist_ok=True); os.makedirs(SD, exist_ok=True)
    TW, TH = 480, 270
    def grab(t):
        p = os.path.join(FD, f"f_{t:08.2f}.jpg")
        if not os.path.exists(p): subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", MP4, "-frames:v", "1", "-vf", f"scale={TW}:{TH}", "-q:v", "4", p])
        return p
    with ThreadPoolExecutor(8) as ex: list(ex.map(grab, [t for n in narr for t in (n["t1"], n["t2"])]))
    font = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 22); fb = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 20)
    LAB, TXT, PER = 30, 34, 8
    for si in range(0, len(narr), PER):
        ch = narr[si:si + PER]; nrow = (len(ch) + 1) // 2
        img = Image.new("RGB", (TW * 4, nrow * (TH + LAB + TXT)), (20, 20, 20)); d = ImageDraw.Draw(img)
        for k, n in enumerate(ch):
            r, c = k // 2, (k % 2) * 2; y = r * (TH + LAB + TXT)
            for j, (t, src) in enumerate([(n["t1"], n["src1"]), (n["t2"], n["src2"])]):
                x = (c + j) * TW
                try: img.paste(Image.open(grab(t)).convert("RGB").resize((TW, TH)), (x, y + LAB))
                except Exception: d.text((x + 20, y + LAB + 100), "프레임 없음", font=font, fill=(255, 0, 0))
                d.text((x + 6, y + 2), f"#{n['idx']} B{n['blk']} {'시작' if j == 0 else '중간'} {mmss(t)}  src {mmss(src) if src is not None else '-'}", font=fb, fill=(255, 230, 80) if j == 0 else (150, 220, 255))
            x0 = c * TW; d.rectangle([x0, y + LAB + TH, x0 + 2 * TW - 2, y + LAB + TH + TXT], fill=(0, 0, 60))
            d.text((x0 + 6, y + LAB + TH + 3), f"[{mmss(n['s'])}-{mmss(n['e'])}] {n['text']}", font=font, fill=(255, 255, 255))
            d.line([x0 + 2 * TW - 1, y, x0 + 2 * TW - 1, y + TH + LAB + TXT], fill=(255, 0, 0), width=3)
        img.save(os.path.join(SD, f"sheet_{si // PER + 1:02d}.jpg"), quality=82)
    say(f"시트 {(len(narr) + PER - 1) // PER}장: {SD} (줄마다 시작·가운데 프레임 — 직접 보고 csv 에 판정)")
    # 훅 첫 10초 0.5초 간격 띠
    ts = [round(x * 0.5, 2) for x in range(20)]
    with ThreadPoolExecutor(8) as ex: ps = list(ex.map(grab, ts))
    st = Image.new("RGB", (TW * 5, (TH + LAB) * 4), (20, 20, 20)); d = ImageDraw.Draw(st)
    for i, (t, p) in enumerate(zip(ts, ps)):
        x, y = (i % 5) * TW, (i // 5) * (TH + LAB)
        try: st.paste(Image.open(p).convert("RGB").resize((TW, TH)), (x, y + LAB))
        except Exception: pass
        w = win_at(t); d.text((x + 6, y + 2), f"{t:.1f}초 src {mmss(w['s'] + (t - w['a']) * 1.05) if w else '-'}", font=fb, fill=(255, 230, 80))
    st.save(os.path.join(SD, "hook_10s.jpg"), quality=82); say(f"훅 띠: {os.path.join(SD, 'hook_10s.jpg')}")
if not fresh:
    o, res = score(CSV); R["verdict"] = {k: v for k, v in res.items()}; say("판정(채운 csv): " + " · ".join(o))
json.dump(R, open(os.path.join(OUT, "sync_check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
open(os.path.join(OUT, "sync_check.txt"), "w", encoding="utf-8").write("\n".join(T) + "\n")
