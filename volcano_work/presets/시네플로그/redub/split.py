# -*- coding: utf-8 -*-
"""남의 몰아보기 영상에서 나레(해설자 목소리)와 드라마 대사를 가른다 → W/narr_blocks.json [{a,b,t,ids}].
10-31 빈센조 때 손으로 한 것을 묶음. whisper 구간은 나레·대사를 한 덩어리로 섞어서 단어 시각으로 다시 끊는다.
  1) 단어 사이 0.3초 미만이면 한 토막(chunks.json) — 단 whisper 구간 경계·문장 끝(.?!)에선 끊는다
  2) 토막마다 resemblyzer 목소리 지문(cemb.npy)
  3) 제브 is_narration(_제브/나레대사구분.json) → cjev_out.jsonl
  4) 제브 0.85 이상·1초 이상 토막의 지문 평균 = 해설자 중심, 중심과 닮은 정도(csim.npy)
  5) 닮음 0.80 이상 = 나레 · 0.70~0.80 은 제브 0.55 이상이거나 짧은 이음말이면 나레
  6) 나레 토막 사이 0.6초 미만이면 한 덩어리
사용: python split.py W   (W 에 asr.json·a16.wav 가 있어야 한다)"""
import json, os, re, subprocess, sys
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
JEV = os.path.expanduser("~/volcano_work/_제브")
LINK = re.compile(r"^(바로|그리고|그런데|하지만|한편|그때|바로 그때|이후|결국|그러자|이때|그날 밤|며칠 뒤|얼마 뒤|곧이어|그러던 중|그 시각|다음 날|잠시 후|그렇게)")


def chunks(W):
    # 10-31 우아한 가: 해설자가 대사 바로 뒤(0.3초 안)에 말을 이어 한 토막에 섞임 → whisper 구간 경계·문장 끝(.?!)에서도 끊는다.
    A = json.load(open(os.path.join(W, "asr.json"), encoding="utf-8")); Wd = A["words"]; cut = set(); j = 0
    for s in A["segments"]:
        while j < len(Wd) and Wd[j]["start"] < s["start"] - 0.05: j += 1
        k = j
        while k < len(Wd) and Wd[k]["start"] < s["end"] + 0.05: k += 1
        if j < len(Wd): cut.add(j)                      # 구간 첫 낱말 앞에서 끊음
        sent = [len(x.split()) for x in re.split(r"(?<=[.?!])\s+", s["text"].strip()) if x.strip()]
        if sum(sent) == k - j:                          # 낱말 수가 맞을 때만 문장 끝을 믿는다
            c = j
            for n in sent[:-1]: c += n; cut.add(c)
        j = k
    C = []
    for i, w in enumerate(Wd):
        if C and i not in cut and w["start"] - C[-1]["b"] < 0.3: C[-1]["b"] = max(C[-1]["b"], w["end"]); C[-1]["t"] += " " + w["word"].strip()
        else: C.append({"a": w["start"], "b": w["end"], "t": w["word"].strip()})
    p = os.path.join(W, "chunks.json")
    if os.path.exists(p) and json.load(open(p, encoding="utf-8")) != C:   # 토막이 바뀌면 지문·제브 저장분은 버린다
        for x in ("cemb.npy", "cjev_out.jsonl"):
            if os.path.exists(os.path.join(W, x)): os.remove(os.path.join(W, x))
    json.dump(C, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    return C


def embed(W, C):
    p = os.path.join(W, "cemb.npy")
    if os.path.exists(p) and len(np.load(p)) == len(C): return np.load(p)
    import soundfile as sf
    from resemblyzer import VoiceEncoder
    f = sf.SoundFile(os.path.join(W, "a16.wav")); sr = f.samplerate; enc = VoiceEncoder("cpu"); E = []
    for k, c in enumerate(C):
        f.seek(int(c["a"] * sr)); x = f.read(int((max(c["b"], c["a"] + 0.5) - c["a"]) * sr), dtype="float32")
        E.append(enc.embed_utterance(x) if len(x) >= int(0.45 * sr) else np.zeros(256, np.float32))
        if k % 500 == 0: print("emb", k, len(C), flush=True)
    E = np.array(E); np.save(p, E); return E


def jev(W, C):
    i, o = os.path.join(W, "cjev_in.jsonl"), os.path.join(W, "cjev_out.jsonl")
    done = {}
    if os.path.exists(o):
        for l in open(o, encoding="utf-8"): d = json.loads(l); done[d["id"]] = d["answers"]["is_narration"]
    if len(done) < len(C):
        with open(i, "w", encoding="utf-8") as f:
            for k, c in enumerate(C): f.write(json.dumps({"id": str(k), "text": c["t"]}, ensure_ascii=False) + "\n")
        subprocess.run(["py", "-3.12", os.path.join(JEV, "거르기.py"), "--spec", os.path.join(JEV, "나레대사구분.json"),
                        "--in", i, "--out", o, "--topic", "드라마 몰아보기 유튜브 영상"], check=True)
        for l in open(o, encoding="utf-8"): d = json.loads(l); done[d["id"]] = d["answers"]["is_narration"]
    return np.array([done.get(str(k), 0.0) for k in range(len(C))])


def main(W):
    C = chunks(W); E = embed(W, C); J = jev(W, C)
    ok = np.linalg.norm(E, axis=1) > 0; dur = np.array([c["b"] - c["a"] for c in C])
    th = 0.85
    if ((J >= th) & ok & (dur >= 1.0)).sum() < 15:   # 11-01 러브 제너레이션: 말하듯 하는 나레라 0.85 넘는 토막이 0개 → 위에서 30개
        cand = np.where(ok & (dur >= 1.0))[0]; th = float(np.sort(J[cand])[-30]) if len(cand) >= 30 else 0.0
        print("제브 문턱 낮춤", th)
    ref = E[(J >= th) & ok & (dur >= 1.0)]
    cen = ref.mean(0); cen /= np.linalg.norm(cen)
    S = np.where(ok, E @ cen / np.maximum(np.linalg.norm(E, axis=1), 1e-6), 0); np.save(os.path.join(W, "csim.npy"), S)
    N = [bool((s >= 0.80) or (0.70 <= s < 0.80 and (j >= 0.55 or (LINK.match(c["t"]) and len(c["t"]) <= 14))))
         for s, j, c in zip(S, J, C)]
    # 문장 끝에서 끊으니 「바로」「곧이어」 같은 짧은 머리말이 따로 떨어져 지문이 흐림 → 바로 뒤가 나레면 나레로
    for k in range(len(C) - 2, -1, -1):
        if not N[k] and N[k + 1] and dur[k] < 1.5 and C[k + 1]["a"] - C[k]["b"] < 0.6 and S[k] >= 0.55 \
                and (LINK.match(C[k]["t"]) or J[k] >= 0.2): N[k] = True
    B = []
    for k, c in enumerate(C):
        if not N[k]: continue
        if B and c["a"] - B[-1]["b"] < 0.6: B[-1]["b"] = c["b"]; B[-1]["t"] += " " + c["t"]; B[-1]["ids"].append(k)
        else: B.append({"a": c["a"], "b": c["b"], "t": c["t"], "ids": [k]})
    json.dump(B, open(os.path.join(W, "narr_blocks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("중심 토막", len(ref), "· 토막", len(C), "나레", sum(N), "· 덩어리", len(B),
          "글자", sum(len(b["t"]) for b in B), "초", round(sum(b["b"] - b["a"] for b in B)))


if __name__ == "__main__":
    main(sys.argv[1])
