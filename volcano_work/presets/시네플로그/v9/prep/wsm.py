# -*- coding: utf-8 -*-
"""로컬 받아쓰기(faster-whisper) → sm.py 와 같은 꼴 {"segments":[{start,end,text,sp}], "words":[{word,start,end,sp,p}]}.
10-23 대작 07 잭 리처: Speechmatics 키가 403(드루와 14편 받아쓰기 뒤 한도) → 이 PC 캐시 모델로 대신. 화자 구분은 없음(sp "S1").
10분 토막마다 _wsm_parts/NNN.json 에 저장해 멈춰도 이어서 한다.
사용: python wsm.py 미디어 출력.json [언어=en] [모델=large-v3-turbo]"""
import json, os, re, subprocess, sys, tempfile
src, out = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else "en"
MODEL = sys.argv[4] if len(sys.argv) > 4 else "mobiuslabsgmbh/faster-whisper-large-v3-turbo"
CH = 600
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
pdir = os.path.join(os.path.dirname(os.path.abspath(out)), "_wsm_parts"); os.makedirs(pdir, exist_ok=True)
from faster_whisper import WhisperModel
m = WhisperModel(MODEL, device="cpu", compute_type="int8", cpu_threads=int(os.environ.get("WSM_THREADS", "6")))
PUN = re.compile(r"^(.*?)([.,!?;:…\"'”’)\]-]*)$")
for k in range(int(dur // CH) + 1):
    pf = os.path.join(pdir, f"{k:03d}.json")
    if os.path.exists(pf): continue
    a = k * CH
    if a >= dur: break
    wav = os.path.join(tempfile.gettempdir(), f"wsm_{os.getpid()}.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(CH), "-i", src, "-map", "0:a:0", "-ac", "1", "-ar", "16000", wav], check=True)
    segs, _ = m.transcribe(wav, language=lang, word_timestamps=True, vad_filter=True, beam_size=5, condition_on_previous_text=False)
    ws = []
    for s in segs:
        for w in s.words or []:
            t = w.word.strip()
            if not t: continue
            mm = PUN.match(t); core, p = mm.group(1), mm.group(2)
            if not core:
                if ws: ws[-1]["p"] += p
                continue
            ws.append({"word": core.lstrip("\"'“‘(["), "start": round(a + w.start, 3), "end": round(a + w.end, 3), "sp": "S1", "p": p})
    os.remove(wav)
    json.dump(ws, open(pf, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"토막 {k} {a:.0f}s 낱말 {len(ws)}", flush=True)
words = []
for f in sorted(os.listdir(pdir)):
    words += json.load(open(os.path.join(pdir, f), encoding="utf-8"))
segs = []; cur = None
for w in words:
    if cur and w["start"] - cur["end"] > 1.0: segs.append(cur); cur = None
    if not cur: cur = {"start": w["start"], "end": w["end"], "text": "", "sp": w["sp"]}
    cur["text"] += ("" if not cur["text"] else " ") + w["word"] + w["p"]; cur["end"] = w["end"]
    if any(c in w["p"] for c in ".?!") and len(cur["text"]) > 40: segs.append(cur); cur = None
if cur: segs.append(cur)
tmp = out + ".tmp"
json.dump({"segments": segs, "words": words}, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
os.replace(tmp, out)
print(out, " 구간", len(segs), "· 낱말", len(words), "· 화자 1(로컬)")
