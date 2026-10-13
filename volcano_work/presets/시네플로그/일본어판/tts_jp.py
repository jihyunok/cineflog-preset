# -*- coding: utf-8 -*-
"""일본어 나레(VOICEVOX 青山龍星 ノーマル) — 자막 덩어리(한 줄 18자 안팎)마다 따로 녹음해 이어 붙인다 → 자막 시각이 정확하다.
narr/nNNN.wav(+ .json: text, chunks=[[글자, 시작, 끝]])"""
import json, os, re, io, wave, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import vv
VID = int(os.environ.get("VID", "13"))  # 10-05 사용자 "1번 줘" = 青山龍星 ノーマル; SPEED = 1.12; PITCH = -0.03
READ = [("IMF", "アイエムエフ"), ("AI", "エーアイ"), ("MGM", "エムジーエム"), ("二〇二五年", "二千二十五年"), ("RFID", "アールエフアイディー")]
MAXC = 18
def chunks(t):
    out = []
    for s in re.findall(r"[^。！？]+[。！？]?", t):
        s = s.strip()
        if not s: continue
        parts = [s]
        while any(len(p.rstrip("。、！？")) > MAXC for p in parts):
            q = []
            for p in parts:
                if len(p.rstrip("。、！？")) <= MAXC: q.append(p); continue
                cut = [m.end() for m in re.finditer("、", p) if 4 <= m.end() <= len(p) - 4]
                k = min(cut, key=lambda c: abs(c - len(p) / 2)) if cut else len(p) // 2
                q += [p[:k], p[k:]]
            parts = q
        out += parts
    return out
def say(s):
    r = s
    for a, b in READ: r = r.replace(a, b)
    return r
def one(q):
    i, text = q["ni"], q["text"]; wav, js = f"narr/n{i:03d}.wav", f"narr/n{i:03d}.json"
    if os.path.exists(js) and json.load(open(js, encoding="utf-8")).get("text") == text and json.load(open(js, encoding="utf-8")).get("vid") == VID: return
    cs = chunks(text); pcm = b""; t = 0.0; meta = []; sr = 48000
    for c in cs:
        w = wave.open(io.BytesIO(vv.synth(say(c), VID, SPEED, PITCH)))
        fr = w.readframes(w.getnframes()); d = w.getnframes() / sr
        gap = 0.22 if c.endswith(("。", "！", "？")) else 0.06
        meta.append([c.rstrip("。、"), round(t, 3), round(t + d, 3)])
        pcm += fr + b"\x00" * (int(sr * gap) * 4); t += d + gap
    raw = f"narr/n{i:03d}_raw.wav"
    with wave.open(raw, "wb") as o: o.setnchannels(2); o.setsampwidth(2); o.setframerate(sr); o.writeframes(pcm)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000", "-ac", "2", wav], check=True)
    os.remove(raw)
    json.dump({"text": text, "vid": VID, "chunks": meta}, open(js, "w", encoding="utf-8"), ensure_ascii=False)
IT = [q for q in json.load(open("items.json", encoding="utf-8")) if q["type"] == "N"]
with ThreadPoolExecutor(2) as ex: list(ex.map(one, IT))
tot = sum(json.load(open(f"narr/n{q['ni']:03d}.json", encoding="utf-8"))["chunks"][-1][2] for q in IT)
print("done", len(IT), "조각", round(tot / 60, 1), "분", "최장 자막", max(len(c[0]) for q in IT for c in json.load(open(f"narr/n{q['ni']:03d}.json", encoding="utf-8"))["chunks"]))
