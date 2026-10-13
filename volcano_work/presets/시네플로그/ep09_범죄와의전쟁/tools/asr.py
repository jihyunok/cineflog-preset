import json, os, subprocess, time, uuid, urllib.request, urllib.error
KEY = open(os.path.expanduser("~/.volcano/keys/groq"), encoding="utf-8").read().strip()
def asr(p):
    b = "----x" + uuid.uuid4().hex; parts = []
    for k, v in [("model","whisper-large-v3"),("response_format","verbose_json"),("temperature","0"),("language","ko"),("timestamp_granularities[]","segment"),("timestamp_granularities[]","word")]:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode()); parts.append(open(p,"rb").read()); parts.append(f"\r\n--{b}--\r\n".encode())
    while True:
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=b"".join(parts), headers={"Authorization":"Bearer "+KEY,"Content-Type":"multipart/form-data; boundary="+b,"User-Agent":"curl/8"}), timeout=300))
        except urllib.error.HTTPError as e:
            m = e.read().decode()[:200]; print("  ", e.code, m, flush=True)
            if e.code == 429: time.sleep(40); continue
            raise
os.makedirs("asr", exist_ok=True)
D = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","src.mp4"],capture_output=True,text=True).stdout)
segs = []
for k in range(int(D // 600) + 1):
    j = f"asr/{k:02d}.json"
    if not os.path.exists(j):
        p = f"asr/{k:02d}.mp3"
        subprocess.run(["ffmpeg","-v","error","-y","-ss",str(k*600),"-t","600","-i","src.mp4","-vn","-ac","1","-ar","16000","-b:a","48k",p], check=True)
        json.dump(asr(p), open(j,"w",encoding="utf-8"), ensure_ascii=False); print(k, "ok", flush=True)
    for s in json.load(open(j, encoding="utf-8"))["segments"]:
        segs.append({"s": round(k*600 + s["start"], 2), "e": round(k*600 + s["end"], 2), "t": s["text"].strip()})
with open("ko.txt", "w", encoding="utf-8") as f:
    for i, s in enumerate(segs, 1):
        f.write(f'{i} {int(s["s"]//3600)}:{int(s["s"]%3600//60):02d}:{s["s"]%60:04.1f} {s["e"]-s["s"]:.1f} {s["t"]}\n')
json.dump(segs, open("ko.json","w",encoding="utf-8"), ensure_ascii=False)
print("segments", len(segs))
