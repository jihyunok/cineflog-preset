# -*- coding: utf-8 -*-
"""아랍어 나레 몰아보기(남의 영상) 가르기 — split.py 방식(목소리 지문 + 제브)을 아랍어 나레에 맞춘 것.
11-12 재혼황후(ملخصات فرح, 이집트 아랍어 나레 + 한국어 드라마 대사) 일본어판 시험 때 만듦.
split.py 와 다른 점
  - 받아쓰기는 language=ar(asr.json). 한국어 대사 자리는 whisper 가 빈 구간으로 내거나 낱말을 거의 안 낸다.
  - 제브 판정 문구는 _제브/나레대사구분_아랍어.json, 이음말(LINK)은 이집트 아랍어.
  - 나레가 거의 쉼 없이 이어져서, 0.6초 미만 틈으로만 이으면 몇 분짜리 덩어리가 된다
    → 한 덩어리 최대 MAXD 초(기본 12)까지만 토막 경계에서 잇는다(번역·녹음·자막을 덩어리마다 맞추기 위함).
  - 토막·지문(chunks.json·cemb.npy)은 split.py 함수를 그대로 쓴다.
사용: python split_ar.py W [MAXD]   (W 에 asr.json·a16.wav)
결과: W/narr_blocks.json [{a,b,t,ids}] · W/csim.npy · W/cjev_out.jsonl"""
import json, os, re, subprocess, sys
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split as SP

JEV = os.path.expanduser("~/volcano_work/_제브")
LINK = re.compile(r"^(و?بعدين|و?بعد كده|لكن|بس|و?فجأة|و?طبعا|و?ساعتها|وهنا|هنا|في الوقت ده|وفي نفس الوقت|في نفس الوقت|على الناحية التانية|و?بالفعل|و?فعلا)")


def jev(W, C):
    i, o = os.path.join(W, "cjev_in.jsonl"), os.path.join(W, "cjev_out.jsonl")
    done = {}
    if os.path.exists(o):
        for l in open(o, encoding="utf-8"): d = json.loads(l); done[d["id"]] = d["answers"]["is_narration"]
    if len(done) < len(C):
        with open(i, "w", encoding="utf-8") as f:
            for k, c in enumerate(C): f.write(json.dumps({"id": str(k), "text": c["t"]}, ensure_ascii=False) + "\n")
        subprocess.run(["py", "-3.12", os.path.join(JEV, "거르기.py"), "--spec", os.path.join(JEV, "나레대사구분_아랍어.json"),
                        "--in", i, "--out", o, "--topic", "한국 드라마 요약 유튜브 영상(이집트 아랍어 나레)"], check=True)
        for l in open(o, encoding="utf-8"): d = json.loads(l); done[d["id"]] = d["answers"]["is_narration"]
    return np.array([done.get(str(k), 0.0) for k in range(len(C))])


def cap(W, B, MAXD):
    """토막 하나가 MAXD 넘는 덩어리(whisper 가 구간을 비워 낱말 사이 0.3초 쉼도 없이 19초씩 이어진 것)를 낱말 경계에서 고르게 쪼갠다.
    목표 지점 ±2.5초 안에서 낱말 사이 틈이 가장 큰 곳. 쪼갠 조각은 같은 토막 번호(ids)를 함께 쓴다(spans 는 합집합이라 그대로 맞음)."""
    Wd = json.load(open(os.path.join(W, "asr.json"), encoding="utf-8"))["words"]; out = []
    for b in B:
        if b["b"] - b["a"] <= MAXD: out.append(b); continue
        ws = [w for w in Wd if b["a"] - 0.01 <= w["start"] < b["b"]]
        n = int(np.ceil((b["b"] - b["a"]) / MAXD)); parts = []; s = 0
        for p in range(1, n):
            tgt = b["a"] + (b["b"] - b["a"]) * p / n
            cand = [k for k in range(s + 1, len(ws)) if abs(ws[k]["start"] - tgt) <= 2.5] or \
                   [min(range(s + 1, len(ws)), key=lambda k: abs(ws[k]["start"] - tgt))]
            k = max(cand, key=lambda k: (ws[k]["start"] - ws[k - 1]["end"]) - 0.05 * abs(ws[k]["start"] - tgt))
            parts.append(ws[s:k]); s = k
        parts.append(ws[s:])
        for j, p in enumerate(parts):
            out.append({"a": b["a"] if j == 0 else p[0]["start"], "b": b["b"] if j == len(parts) - 1 else p[-1]["end"],
                        "t": " ".join(w["word"] for w in p), "ids": list(b["ids"])})
    return out


def main(W, MAXD=12.0):
    MAXD = float(MAXD)
    C = SP.chunks(W); E = SP.embed(W, C); J = jev(W, C)
    ok = np.linalg.norm(E, axis=1) > 0; dur = np.array([c["b"] - c["a"] for c in C])
    th = 0.85
    if ((J >= th) & ok & (dur >= 1.0)).sum() < 15:
        cand = np.where(ok & (dur >= 1.0))[0]; th = float(np.sort(J[cand])[-30]) if len(cand) >= 30 else 0.0
        print("제브 문턱 낮춤", th)
    ref = E[(J >= th) & ok & (dur >= 1.0)]
    cen = ref.mean(0); cen /= np.linalg.norm(cen)
    S = np.where(ok, E @ cen / np.maximum(np.linalg.norm(E, axis=1), 1e-6), 0); np.save(os.path.join(W, "csim.npy"), S)
    N = [bool((s >= 0.80) or (0.70 <= s < 0.80 and (j >= 0.55 or (LINK.match(c["t"]) and len(c["t"]) <= 14))))
         for s, j, c in zip(S, J, C)]
    for k in range(len(C) - 2, -1, -1):
        if not N[k] and N[k + 1] and dur[k] < 1.5 and C[k + 1]["a"] - C[k]["b"] < 0.6 and S[k] >= 0.55 \
                and (LINK.match(C[k]["t"]) or J[k] >= 0.2): N[k] = True
    # 말 언어: 대사는 한국어라 ar 받아쓰기가 아랍어 낱말을 낸 토막 + 해설자와 닮음 0.65 이상이면 나레
    # (11-12 재혼황후: 「الطائر اللي انقذها بنتلاحظ」 같은 해설 토막 7개가 닮음 0.70~0.80·제브 0.06~0.51 로 빠져 아랍어 목소리가 남을 뻔)
    AR = re.compile(r"[؀-ۿ]{2,}")
    for k, c in enumerate(C):
        if not N[k] and S[k] >= 0.65 and len(AR.findall(c["t"])) >= 1: N[k] = True; print("말 언어로 나레", k, round(c["a"], 1), c["t"])
    B = []
    for k, c in enumerate(C):
        if not N[k]: continue
        if B and c["a"] - B[-1]["b"] < 0.6 and c["b"] - B[-1]["a"] <= MAXD:
            B[-1]["b"] = c["b"]; B[-1]["t"] += " " + c["t"]; B[-1]["ids"].append(k)
        else: B.append({"a": c["a"], "b": c["b"], "t": c["t"], "ids": [k]})
    B = cap(W, B, MAXD)
    json.dump(B, open(os.path.join(W, "narr_blocks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    d = np.array([b["b"] - b["a"] for b in B])
    print("중심 토막", len(ref), "· 토막", len(C), "나레", sum(N), "· 덩어리", len(B),
          "글자", sum(len(b["t"]) for b in B), "초", round(d.sum()), "· 덩어리 길이 중앙", round(float(np.median(d)), 1), "최대", round(float(d.max()), 1))


if __name__ == "__main__":
    main(*sys.argv[1:])
