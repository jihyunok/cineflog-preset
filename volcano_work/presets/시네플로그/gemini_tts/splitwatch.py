# gem/bKK_n0_n1.wav 가 새로 생기면 gem_split → narr/nNNN.wav·json (편 폴더 안에서) · 끝나면 gem/bKK.done
import glob, os, re, subprocess, sys, time
ROOT = os.environ.get("CINE_WORK") or ("D:/cine_work" if os.path.isdir("D:/") else os.path.expanduser("~/cine_work")); T = ROOT + "/tts"
while True:
    for w in sorted(glob.glob(ROOT + "/ep*/gem/b*.wav")):
        if os.path.exists(w + ".done"): continue
        m = re.search(r"b\d+_(\d+)_(\d+)\.wav$", w); ep = os.path.dirname(os.path.dirname(w))
        r = subprocess.run([sys.executable, T + "/gem_split.py", "gem/" + os.path.basename(w), m[1], m[2]], cwd=ep, capture_output=True, text=True, encoding="utf-8", errors="replace")
        c = subprocess.run([sys.executable, T + "/gem_check.py", "gem/" + os.path.basename(w), m[1], m[2]], cwd=ep, capture_output=True, text=True, encoding="utf-8", errors="replace")
        open(w + ".done", "w", encoding="utf-8").write(r.stdout[-2000:] + r.stderr[-2000:] + "\n--check--\n" + c.stdout[-3000:])
        print(time.strftime("%H:%M"), w, "rc", r.returncode, c.stdout.strip().splitlines()[-1:] if c.stdout else "", flush=True)
    time.sleep(20)
