# -*- coding: utf-8 -*-
"""시네플로그 롱폼 빌더 (17편: 1920x802 원본 · 박힌 자막 y640~780 → crop 1512x630 위쪽(27% 확대) · END 4895 · 금지 구간 FORBID | 13편: 1918x802 원본 · 박힌 한국어 자막 y642~754 → crop 1518x632 위쪽 · 금지 구간(앞 로고·오프닝 크레딧·제목 카드) · 자막 N 경기천년제목 84 / D 스타일리시 88 / CINEFLOG 오른쪽 위 회색 · PREP=1 이면 대사 컷만 자른다 | 07편: 1920x800 원본 · 박힌 한국어 자막(y655~780)을 잘라냄(위쪽 1536x640) · 04편: 노란 자막 처리 없음 · 자막 없는 원본 소리 컷 · END 환경변수) — 무비마스터 공정사용 규칙
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
END = float(os.environ.get("END", "4895"))   # 크레딧 전까지
W, H, BAR = 1920, 1080, 140
VF_BASE = "crop=1512:630:204:4,scale=1920:800,eq=saturation=1.12:contrast=1.04:brightness=0.01,hue=h=4"
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
        lo, hi = a, min(b + ext, END)
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
                if not fell: a, b, ext, fell = 60, END, 0, True      # 영화 전체(크레딧 전)에서 빈 곳을 찾는다
                else: sys.exit(f"컷이 모자람: {a}-{b} n={n}")
    return out

def yellow(s, e): return False
VF_ZOOM = None
def clip(path, s, ls, speed, mirror, gain_db, lo):
    if os.path.exists(path): return
    vf = (VF_ZOOM if yellow(s, s + ls) else VF_BASE) + (",hflip" if mirror else "") + f",pad={W}:{H}:0:{BAR}:black,setpts=PTS/{speed},fps=30,format=yuv420p"
    af = (f"atempo={speed}," if speed != 1 else "") + f"volume={gain_db}dB" + (",alimiter=limit=0.9" if gain_db > 0 else "") + ",aresample=48000"
    subprocess.run(FF + ["-ss", f"{s:.3f}", "-t", f"{ls:.3f}", "-i", SRC, "-vf", vf, "-af", af, "-t", f"{lo:.3f}",
                         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "pcm_s16le", "-ac", "2", path], check=True)

segs = []
plan = []
def dclip(tag, d):
    p = f"blocks/{tag}.mkv"; 0 and clip(p, d["s"], d["d"], 1, d["mirror"], 17.5 if d["ko"] else 6, d["d"])
    plan.append({"blk": tag, "type": "D", "src": [d["s"], round(d["s"] + d["d"], 2)], "mirror": d["mirror"]})
    segs.append(("D", p, {"ko": d["ko"]}))

def nseg(tag, nw, nj, a, b):
    nd = len(next(q["text"] for q in IT if q.get('ni') and f"n{q['ni']:03d}" == tag)) / 470 * 60; total = nd + 0.12
    n = max(1, math.ceil(total / (MAXC / SPEED))); lo = total / n; ls = lo * SPEED
    picks = pick(a, b, n, ls); cl = []
    for k, (s0, e0) in enumerate(picks):
        p = ""; cl.append(p)
        plan.append({"blk": tag, "type": "N", "src": [round(s0, 2), round(e0, 2)], "mirror": k % 2 == 1})
    out = f"blocks/{tag}.mkv"
    if False:
        lst = f"blocks/{tag}.txt"; open(lst, "w").write("".join(f"file '../{c}'\n" for c in cl))
        subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", lst, "-i", nw, "-filter_complex",
                             "[1:a]adelay=60|60,apad[n];[0:a][n]amix=inputs=2:normalize=0:duration=first[a]",
                             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "pcm_s16le", out], check=True)
    segs.append(("N", out, {"json": nj}))

IT = json.load(open("items.json", encoding="utf-8"))
FORBID = [(0, 238), (398, 413), (2108, 2123), (3950, 3967), (4760, 4783)]   # 로고·연설·영어 안내문·제목 카드·「두 달 전」(~3:58) / 요일 카드 3개(한국어 자막이 그림 안) / THANK YOU 호출명 글자(1:19:20~1:19:43)
used[:] = [(q["s"], q["s"] + q["d"]) for q in IT if q["type"] == "D"] + FORBID
if os.environ.get("PREP"):
    for q in IT:
        if q["type"] == "D": dclip(f"d{int(q['s']*100):07d}", q)
    print("대사 컷", sum(q["type"] == "D" for q in IT)); sys.exit()
DSET = set(used)
def free(s, e):
    return all(e + GAP <= a or s >= b + GAP for a, b in used)
for q in IT:
    if q["type"] == "N":
        nseg(f"n{q['ni']:03d}", f"narr/n{q['ni']:03d}.wav", f"narr/n{q['ni']:03d}.json", q["rng"][0], q["rng"][1])
    else:
        dclip(f"d{int(q['s']*100):07d}", q)
json.dump(plan, open("dry_plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# ── 3초 규칙 검사
srcs = sorted(p["src"] for p in plan)
bad = [(a, b) for a, b in srcs if (b - a) > (3.95 if False else 4.0)]
close = [(srcs[i], srcs[i + 1]) for i in range(len(srcs) - 1) if srcs[i + 1][0] - srcs[i][1] < GAP - 0.01]
print(f"컷 {len(plan)}개 · 3초 넘는 컷 {sum(1 for a,b in srcs if b-a>2.95)}개(대사 변조 허용) · 간격 3초 미만 {len(close)}개")

