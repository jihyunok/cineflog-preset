# -*- coding: utf-8 -*-
"""Speechmatics 받아쓰기 — 문장부호·화자까지 → {"segments":[{start,end,text,sp}], "words":[{word,start,end,sp,p}]} (+ 원본 json-v2 는 출력_raw.json).
10-14 시네플로그 01·02 다시 만들기(사용자 "스피치매틱스로하는거 맞지?" — 낱말 시각은 Speechmatics). 17 그레이하운드 src_sm.json 과 같은 꼴(words 는 문장부호 없이, p 에 붙은 부호).
사용: python sm.py 미디어 출력.json [언어=en] [--diar]"""
import json, os, subprocess, sys, tempfile, time, urllib.request, urllib.error, uuid
src, out = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else "en"
DIAR = "--diar" in sys.argv
key = (os.environ.get("SPEECHMATICS_API_KEY") or open(os.path.expanduser("~/.volcano/keys/speechmatics"), encoding="utf-8").read()).strip()
API = "https://asr.api.speechmatics.com/v2"; H = {"Authorization": "Bearer " + key}
raw = out[:-5] + "_raw.json"
if not os.path.exists(raw):
    mp3 = os.path.join(tempfile.gettempdir(), f"sm_{uuid.uuid4().hex[:8]}.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0:a:0", "-ac", "1", "-ar", "16000", "-b:a", "48k", mp3], check=True)
    tc = {"language": lang, "operating_point": "enhanced"}
    if DIAR: tc["diarization"] = "speaker"
    cfg = json.dumps({"type": "transcription", "transcription_config": tc})
    b = "----sm" + uuid.uuid4().hex
    body = b"".join([f"--{b}\r\nContent-Disposition: form-data; name=\"config\"\r\n\r\n{cfg}\r\n".encode(),
                     f"--{b}\r\nContent-Disposition: form-data; name=\"data_file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode(), open(mp3, "rb").read(), f"\r\n--{b}--\r\n".encode()])
    os.remove(mp3)
    for k in range(5):
        try:
            jid = json.loads(urllib.request.urlopen(urllib.request.Request(API + "/jobs", data=body, headers={**H, "Content-Type": "multipart/form-data; boundary=" + b}), timeout=900).read().decode())["id"]; break
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:300]
            if e.code in (429, 500, 502, 503) and k < 4: time.sleep(20); continue
            sys.exit(f"Speechmatics 접수 실패 {e.code} {msg}")
    print("job", jid, "…", flush=True)
    def get(url):
        for k in range(10):
            try: return urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=300).read().decode()
            except Exception:
                if k == 9: raise
                time.sleep(10 + 5 * k)
    while True:
        st = json.loads(get(f"{API}/jobs/{jid}"))["job"]["status"]
        if st != "running": break
        print(".", end="", flush=True); time.sleep(15)
    if st != "done": sys.exit(f"Speechmatics 실패 {jid} {st}")
    open(raw, "w", encoding="utf-8").write(get(f"{API}/jobs/{jid}/transcript?format=json-v2")); print(" done")
R = json.load(open(raw, encoding="utf-8"))["results"]
words = []
for it in R:
    alt = (it.get("alternatives") or [{}])[0]
    if it["type"] == "word": words.append({"word": alt.get("content", ""), "start": round(it["start_time"], 3), "end": round(it["end_time"], 3), "sp": alt.get("speaker", ""), "p": ""})
    elif it["type"] == "punctuation" and words: words[-1]["p"] += alt.get("content", "")
segs = []; cur = None
for w in words:
    if cur and (w["start"] - cur["end"] > 1.0 or w["sp"] != cur["sp"]): segs.append(cur); cur = None
    if not cur: cur = {"start": w["start"], "end": w["end"], "text": "", "sp": w["sp"]}
    cur["text"] += ("" if not cur["text"] or lang in ("ja", "cmn", "yue") else " ") + w["word"] + w["p"]; cur["end"] = w["end"]
    if any(c in w["p"] for c in ".?!") and len(cur["text"]) > 40: segs.append(cur); cur = None
if cur: segs.append(cur)
json.dump({"segments": segs, "words": words}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(out, " 구간", len(segs), "· 낱말", len(words), "· 화자", len({w["sp"] for w in words}))
