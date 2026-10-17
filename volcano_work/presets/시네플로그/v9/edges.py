# -*- coding: utf-8 -*-
"""대사 창 가장자리를 실제 말소리에 맞춘다 (10-13 16 핀치 올린 뒤 "단어가 짤리는거 또있었어" / "처음부터 그렇게 세팅을하지말아야지").
16 핀치는 받아쓰기(Groq) 낱말 시각이 0.1~0.3초 일러 대사 창이 영어 낱말 한가운데서 잘렸다(4:38 loves · 12:53 Hang · 21:03 Overpass 등 23곳).
판정 잣대: 원본 가운데 소리((L+R)/2, 5.1 이면 FC) 300~3400Hz 10ms 크기 + 낱말 시각(Speechmatics).
 - 시작: 이 줄 첫 낱말 앞 조용한 곳(앞 줄 낱말과 사이 가장 조용한 곳)에서 끊는다.
 - 끝: 이 줄 끝 낱말 소리가 실제로 잦아들 때까지 늘린다. 다음 줄 첫 낱말이 바로 붙어 있으면 그 사이 가장 조용한 곳.
모듈: Env(src).snap(s, e) → (s2, e2, 메모) · Env(src).edge_bad(t, side) → 문제 설명 또는 None
CLI: python edges.py check windows.json 원본.mp4 낱말.json [--slen-rate 1.05]   (대사 창 가장자리 검사)"""
import re, json, os, subprocess, sys
import numpy as np
SR = 16000; HOP = 0.01; N = int(SR * HOP)

def band_env(src, cache=None):
    """원본 전체의 말소리 띠(300~3400Hz) 크기 dB, 10ms 칸. cache(.npy) 있으면 그걸."""
    cache = cache or os.path.splitext(os.path.basename(src))[0] + "_band.npy"
    if os.path.exists(cache): return np.load(cache)
    ch = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=channels", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip()
    ch = re.match(r"\d+", ch).group() if re.match(r"\d+", ch or "") else ""      # ★10-16 04v2 ac3 원본은 "2," 로 나와 int 가 죽었다
    pan = "pan=mono|c0=c2" if ch and int(ch) >= 6 else "pan=mono|c0=0.5*c0+0.5*c1"       # 5.1 이면 가운데(FC) 채널에 대사
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-map", "0:a:0", "-af", f"{pan},highpass=f=300,lowpass=f=3400", "-ar", str(SR), "-f", "f32le", "-"], stdout=subprocess.PIPE)
    out = []
    while True:
        b = p.stdout.read(N * 4 * 6000)
        if not b: break
        x = np.frombuffer(b[:len(b) // (N * 4) * N * 4], np.float32)
        out.append(20 * np.log10(np.sqrt((x.reshape(-1, N) ** 2).mean(1) + 1e-12)))
    db = np.concatenate(out).astype(np.float32); np.save(cache, db); return db

def load_words(p):
    """[(시작, 끝, 낱말)] — src_words.json([[s,e,w]]) 이나 asr.json({"words":[{start,end,word}]}) 둘 다"""
    d = json.load(open(p, encoding="utf-8"))
    if isinstance(d, dict): d = d["words"]
    W = [(float(w["start"]), float(w["end"]), w["word"]) if isinstance(w, dict) else (float(w[0]), float(w[1]), w[2]) for w in d]
    return sorted(w for w in W if w[1] >= w[0])

class Env:
    def __init__(self, src, words, cache=None):
        self.db = band_env(src, cache); self.W = words if not isinstance(words, str) else load_words(words)
        self.ws = np.array([w[0] for w in self.W]); self.we = np.array([w[1] for w in self.W])
        self.sm = np.convolve(self.db, np.ones(3) / 3, "same")
    def k(self, t): return int(min(max(t / HOP, 0), len(self.db) - 1))
    def floor_peak(self, s, e):
        a, b = self.k(s - 2), self.k(e + 2); fl = float(np.percentile(self.db[a:b], 10)) if b > a else -60
        ins = [(x, y) for x, y, _ in self.W if s - 0.05 <= (x + y) / 2 <= e + 0.05]
        pk = float(np.percentile(np.concatenate([self.db[self.k(x):self.k(y) + 1] for x, y in ins]), 90)) if ins else fl + 20
        return fl, pk
    def thr(self, s, e):
        fl, pk = self.floor_peak(s, e); return max(fl + 6, fl + 0.3 * (pk - fl))
    def words_in(self, s, e): return [w for w in self.W if s - 0.05 <= (w[0] + w[1]) / 2 <= e + 0.05]
    def quiet_min(self, a, b):
        ka, kb = self.k(a), self.k(b)
        if kb <= ka: return a
        return (ka + int(np.argmin(self.sm[ka:kb + 1]))) * HOP

    def snap(self, s, e, maxlen=5.9):
        """대사 줄 [s,e](대략) → 말소리에 맞춘 (s2, e2, 메모). 이 줄 낱말 = 가운데가 [s,e] 안인 낱말."""
        ins = self.words_in(s, e)
        if not ins: return s, e, "낱말 없음"
        f, l = ins[0], ins[-1]; th = self.thr(f[0], l[1])
        pv = max((w for w in self.W if w[1] <= f[0] + 0.02 and w is not f and w[0] < f[0]), key=lambda w: w[1], default=None)
        nx = min((w for w in self.W if w[0] >= l[1] - 0.02 and w is not l and w[0] > l[0]), key=lambda w: w[0], default=None)
        # 받아쓰기 낱말은 서로 딱 붙어 나오고 시각도 0.1~0.3초 틀린다 → 앞 낱말 꼬리·뒤 낱말 머리 쪽까지 찾되, 조용한 칸이 이어져야 끊는다
        lo = f[0] - 0.6 if not pv else max(f[0] - 0.6, pv[0] + 0.6 * (pv[1] - pv[0]))
        hi = l[1] + 0.9 if not nx else min(l[1] + 0.9, nx[0] + 0.4 * (nx[1] - nx[0]))
        # 시작: 첫 낱말 앞으로 걸어가며 50ms 넘게 조용한 곳 → 그 뒤 소리 시작 0.06초 앞
        k = self.k(f[0] + 0.05); s2 = None
        while k * HOP > lo:
            if (self.db[max(0, k - 5):k] < th).all(): s2 = max(lo, k * HOP - 0.06); break
            k -= 1
        glued = []
        if s2 is None:                     # 조용한 곳이 없음(배경음·환호) → 가장 조용한 곳, 단 첫 낱말 시작보다 0.04초는 앞
            s2 = min(self.quiet_min(max(lo, pv[1] - 0.05) if pv else lo, f[0] + 0.03), f[0] - 0.04)
            if pv: s2 = max(s2, pv[1] + 0.03)
            glued.append("앞 붙음")
        # 끝: 끝 낱말 뒤로 걸어가며 60ms 넘게 조용한 곳 → 0.08초 여유(다음 낱말이 붙어 있으면 그 조용한 곳 안에서)
        k = self.k(max(l[0], l[1] - 0.12)); e2 = None
        while k * HOP < hi:
            if (self.db[k:k + 6] < th).all(): e2 = min(k * HOP + 0.08, k * HOP + 0.03 if nx and nx[0] < k * HOP + 0.2 else 9e9); break
            k += 1
        if e2 is None:                     # 조용한 곳이 없음 → 가장 조용한 곳, 단 끝 낱말 끝보다 0.06초는 뒤(16→17 「job」 끝 잘림)
            e2 = max(self.quiet_min(l[1] - 0.05, min(hi, nx[0] + 0.05) if nx else hi), l[1] + 0.06)
            if nx: e2 = min(e2, nx[0] - 0.03)
            glued.append("뒤 붙음")
        if e2 - s2 > maxlen: glued.append(f"길다 {e2 - s2:.1f}초")
        return round(s2, 3), round(e2, 3), " ".join(glued)       # 붙음 = 쉼 없이 이웃 줄과 이어짐 → 계획에서 이웃 줄과 한 창으로 묶거나 버린다

    def edge_bad(self, t, side, s=None, e=None):
        """가장자리 t 에서 말이 잘리나. side='s'(창 시작)·'e'(창 끝). 16 핀치 23곳을 잡은 잣대 + 낱말 시각이 어긋난 경우."""
        k = self.k(t); c = float(self.db[max(0, k - 1):k + 2].max()); lo = float(self.db[max(0, k - 50):k + 50].min())   # ±10ms — ±30ms 는 바로 뒤 환호성 시작까지 잡았다(17 「We got him」)
        th = self.thr(s if s is not None else t - 1, e if e is not None else t + 1)
        hit = [w for w in self.W if w[1] - w[0] <= 1.2 and w[0] < t - 0.03 and w[1] > t + 0.03]
        if hit and c > -38 and c - lo > 12: return f"낱말 「{hit[0][2]}」 가운데 ({c:.0f}dB)"
        near = [w for w in self.W if (side == "e" and 0 <= w[1] - t < 0.25 and w[0] < t + 0.05) or (side == "s" and 0 <= t - w[0] < 0.25 and w[1] > t - 0.05)]
        if near and c >= th and c > -38 and float(self.db[k:k + 3].mean() if side == "e" else self.db[max(0, k - 3):k].mean()) >= th:
            return f"말소리 속 「{near[0][2]}」 ({c:.0f}dB ≥ {th:.0f})"
        return None

def check(WN, env, rate=1.05):
    """대사 창(kind D) 가장자리 검사 → [(창 번호, 화면 시각, 쪽, 설명)]"""
    out = []
    for i, w in enumerate(WN):
        if w["kind"] != "D": continue
        s = w["s"] - w.get("pre", 0); e = s + (w["b"] - w["a"] - w.get("hold", 0)) * w.get("rate", 1.0)     # drate.py: 대사 창도 배속(10-14)
        for side, t in (("s", s), ("e", e)):
            why = env.edge_bad(t, side, s, e)
            if why: out.append((i, w["a"] if side == "s" else w["b"], side, why + (" · " + w.get("ko", "") if w.get("ko") else "")))
    return out

def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
if __name__ == "__main__":
    if sys.argv[1] == "check":
        WN = json.load(open(sys.argv[2], encoding="utf-8")); env = Env(sys.argv[3], sys.argv[4])
        R = check(WN, env)
        for i, t, side, why in R: print(f"  {mm(t)} 창{i} {'시작' if side == 's' else '끝'} {why}")
        print("대사 창 가장자리 말 잘림", len(R))
