# -*- coding: utf-8 -*-
"""runs.json → 벤치 편집표(edl.json): 벤치 전 구간을 (b0,b1,s0) 컷으로. 비는 곳은 앞 컷을 이어 쓴다(같은 원본 흐름).
그다음 벤치 소리와 원본 소리를 0.25초마다 비교 → 원본 소리(O) / 나레(N) 표시(audio.json)."""
import json, re, subprocess, numpy as np
R = [r for r in json.load(open("runs.json")) if r["ok"]]
END_B = 5764 / 4
# 같은 오프셋 run 합치기
segs = []
for r in sorted(R, key=lambda r: r["b0"]):
    off = r["s0"] - r["b0"]
    if segs and abs(segs[-1]["off"] - off) < 0.6 and r["b0"] - segs[-1]["b1"] < 6 and r["flip"] == segs[-1]["flip"]:
        segs[-1]["b1"] = r["b1"]
    else:
        segs.append({"b0": r["b0"], "b1": r["b1"], "off": off, "flip": r["flip"]})
# 빈 곳: 앞 컷 연장(맨 앞은 뒤 컷 당김)
for a, b in zip(segs, segs[1:]): a["b1"] = b["b0"]
segs[0]["b0"] = 0.0; segs[-1]["b1"] = END_B
# 장면 전환에 붙이기(원본 시간 기준 0.3초 안)
cuts = np.array([float(x) for x in re.findall(r"(?:pts_time:)?(\d+\.\d+)", open("scenes.txt").read())])
for a, b in zip(segs, segs[1:]):
    t = b["b0"]; s_prev = t + a["off"]; s_next = t + b["off"]
    for cand in (s_next, s_prev):
        k = np.abs(cuts - cand).argmin()
        if abs(cuts[k] - cand) < 0.3:
            nt = t + (cuts[k] - cand); a["b1"] = b["b0"] = round(nt, 3); break
segs = [s for s in segs if s["b1"] - s["b0"] > 0.05]
for s in segs: s["s0"] = round(s["b0"] + s["off"], 3); s["d"] = round(s["b1"] - s["b0"], 3)
json.dump(segs, open("edl.json", "w"), indent=0)
print("컷", len(segs), "평균", round(np.mean([s["d"] for s in segs]), 2), "초 · 최장", round(max(s["d"] for s in segs), 1))

# ── 소리 비교
def pcm(src, ss=None):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True)
    return np.frombuffer(p.stdout, np.int16).astype(np.float32) / 32768
ab = pcm("bench/bench.mp4"); asrc = pcm("C:/Users/uere/Downloads/그레이하운드.mp4")
SR = 8000; WIN = 2048
def spec(x):
    if len(x) < WIN: x = np.pad(x, (0, WIN - len(x)))
    f = np.abs(np.fft.rfft(x[:WIN] * np.hanning(WIN)))
    bands = np.add.reduceat(f, np.geomspace(4, 1024, 33).astype(int)[:-1])
    return np.log(bands + 1e-4)
lab = []
for t in np.arange(0, END_B - 0.3, 0.25):
    s = next((g for g in segs if g["b0"] <= t < g["b1"]), segs[-1])
    st = t + s["off"]
    a = ab[int(t * SR): int(t * SR) + WIN]; b = asrc[int(st * SR): int(st * SR) + WIN]
    ea = float(np.sqrt(np.mean(a ** 2)) + 1e-6); eb = float(np.sqrt(np.mean(b ** 2)) + 1e-6)
    c = float(np.corrcoef(spec(a), spec(b))[0, 1]) if len(b) else 0
    lab.append({"t": round(float(t), 2), "c": round(c, 3), "ea": round(20 * np.log10(ea), 1), "eb": round(20 * np.log10(eb), 1)})
json.dump(lab, open("audio.json", "w"), indent=0)
print("창", len(lab), "닮음 0.8+", sum(x["c"] > 0.8 for x in lab))
