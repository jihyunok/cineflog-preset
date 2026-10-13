# -*- coding: utf-8 -*-
"""나레 조각마다 Groq 낱말 시각으로 글자 시각(st/en)을 다시 맞춘다 — gem_split json 이 어긋난 조각(10-12 "1분25초부분글자 안맞아").
대본 글자 ↔ 받아쓴 글자를 difflib 로 짝짓고, 짝 없는 글자는 앞뒤 사이로 채움. 옛 json 은 narr/nNNN.json.bak. 결과: 조각별 최대 어긋남."""
import difflib, json, os, re, shutil, time, uuid, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
KEY = open(os.path.expanduser("~/.volcano/keys/groq"), encoding="utf-8").read().strip()
def asr(p):
    b = "----x" + uuid.uuid4().hex; parts = []
    for k, v in [("model", "whisper-large-v3"), ("response_format", "verbose_json"), ("temperature", "0"), ("language", "ko"), ("timestamp_granularities[]", "word")]:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode())
    parts.append(open(p, "rb").read()); parts.append(f"\r\n--{b}--\r\n".encode())
    for _ in range(20):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=b"".join(parts),
                headers={"Authorization": "Bearer " + KEY, "Content-Type": "multipart/form-data; boundary=" + b, "User-Agent": "curl/8"}), timeout=300))
        except urllib.error.HTTPError as e:
            e.read(); time.sleep(30 if e.code == 429 else 5)
    raise RuntimeError(p)
def norm(c): return bool(re.match(r"[0-9A-Za-z가-힣]", c))
def one(i):
    j = f"narr/n{i:03d}.json"; w = f"narr/n{i:03d}.wav"; cj = f"narr/n{i:03d}_asr.json"
    if not os.path.exists(cj):
        import subprocess
        m = f"narr/_t{i:03d}.mp3"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", w, "-ac", "1", "-ar", "16000", "-b:a", "64k", m], check=True)
        json.dump(asr(m), open(cj, "w", encoding="utf-8"), ensure_ascii=False); os.remove(m)
    words = json.load(open(cj, encoding="utf-8")).get("words", [])
    if not os.path.exists(j + ".bak"): shutil.copy(j, j + ".bak")
    al = json.load(open(j + ".bak", encoding="utf-8")); chars = al["chars"]
    # 받아쓴 글자열 + 글자별 시각(낱말 안에서 고르게)
    W = []; WT = []
    for x in words:
        cs = [c for c in x["word"] if norm(c)]
        for k, c in enumerate(cs):
            W.append(c); WT.append((x["start"] + (x["end"] - x["start"]) * k / len(cs), x["start"] + (x["end"] - x["start"]) * (k + 1) / len(cs)))
    S = [(k, c) for k, c in enumerate(chars) if norm(c)]
    sm = difflib.SequenceMatcher(None, [c for _, c in S], W, autojunk=False)
    st = [None] * len(chars); en = [None] * len(chars)
    for a, b, n in sm.get_matching_blocks():
        for t in range(n): k = S[a + t][0]; st[k], en[k] = WT[b + t]
    known = [k for k in range(len(chars)) if st[k] is not None]
    if len(known) < max(3, len(S) * 0.4): return i, None          # 받아쓰기가 너무 달라 옛 것 유지
    for k in range(len(chars)):
        if st[k] is None:
            p = max([q for q in known if q < k], default=None); n_ = min([q for q in known if q > k], default=None)
            if p is None: st[k] = en[k] = max(0, st[n_] - 0.05 * (n_ - k))
            elif n_ is None: st[k] = en[k] = en[p] + 0.05 * (k - p)
            else: f = (k - p) / (n_ - p); st[k] = en[k] = en[p] + (st[n_] - en[p]) * f
    off = max(abs(a - b) for a, b in zip(st, al["st"]))
    al["st"], al["en"] = [round(x, 3) for x in st], [round(x, 3) for x in en]
    json.dump(al, open(j, "w", encoding="utf-8"), ensure_ascii=False)
    return i, round(off, 2)
ids = sorted(int(f[1:4]) for f in os.listdir("narr") if re.match(r"n\d{3}\.wav$", f))
with ThreadPoolExecutor(4) as ex: R = list(ex.map(one, ids))
bad = [(i, o) for i, o in R if o is None or o > 0.6]
print("조각", len(R), "· 0.6초 넘게 어긋났던 조각", len([1 for i, o in R if o and o > 0.6]), "· 받아쓰기 실패", [i for i, o in R if o is None])
print(sorted(bad, key=lambda x: -(x[1] or 99))[:20])
