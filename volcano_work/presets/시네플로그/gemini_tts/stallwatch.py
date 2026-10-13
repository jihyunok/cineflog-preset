# READY 편 중 녹음이 남았는데 gem wav 가 40분 새로 안 생기면 STALL 로 끝남 · 다 끝나면 ALL TTS DONE
import glob, json, os, time
R = os.environ.get("CINE_WORK") or ("D:/cine_work" if os.path.isdir("D:/") else os.path.expanduser("~/cine_work"))
while True:
    eps = [d for d in glob.glob(R + "/ep*") if os.path.isdir(d)]
    pend = [d for d in eps if os.path.exists(d + "/READY") and len(glob.glob(d + "/gem/b*.wav")) < len(json.load(open(d + "/batches.json", encoding="utf-8")))]
    wavs = glob.glob(R + "/ep*/gem/b*.wav"); age = time.time() - max(os.path.getmtime(w) for w in wavs)
    if pend and age > 2400: print("STALL", [os.path.basename(p) for p in pend], int(age), flush=True); break
    if not pend and all(os.path.exists(d + "/READY") for d in eps): print("ALL TTS DONE", flush=True); break
    time.sleep(120)
