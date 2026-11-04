# -*- coding: utf-8 -*-
# 25 어웨어니스: 나레 → narr_en.json(영어 뜻, narr_pic 관문용) + emph.json(지무비식 강조: 나레 핵심 말·감정, 노랑 대사) — agy 한 번씩
import json, os, re, subprocess
W = "D:/cine_work/ep25_어웨어니스"
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
ns = {}; exec(open(f"{W}/script.py", encoding="utf-8").read(), ns)
NT = [x[1] for x in ns["S"] if x[0] == "N"]
DT = [x[2] for x in ns["S"] if x[0] == "D"]
def ask(p):
    r = subprocess.run([AGY, "-p", p + "\n도구를 쓰지 말고 답해줘.", "--print-timeout", "600s"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout
body = "\n".join(f"{i}\t{t}" for i, t in enumerate(NT, 1))
out = ask("영화 「Awareness」(2023) 리뷰 나레이션이다. 줄마다 자연스러운 영어 한 문장으로 옮겨라(인물: Ian(이안, a teen who projects illusions), Vicente(비센테, the man who raised him), Adriana(아드리아나, Dr. Levin of the Agency), the Perceptor(인지자), Esther(에스테르), Ursula Kominsky(우르술라)). 출력은 `번호\\t영어` 만.\n\n" + body)
en = {m.group(1): m.group(2).strip() for m in re.finditer(r"^(\d+)\t(.+)$", out, re.M)}
json.dump(en, open(f"{W}/narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
out = ask("아래 영화 리뷰 나레 줄마다, 화면 자막에서 크게 강조할 핵심 말(그 줄 글 안에 **글자 그대로** 있는 2~12자 토막)과 감정 하나를 골라라. "
          "감정은 emotion(뭉클·슬픔) · reveal(사실이 드러남) · twist(반전·뜻밖) · grad_slant(보통 강조) · threat(불안·위기) 중 하나. 강조할 게 없는 줄은 빼라. "
          "출력은 `번호\\t핵심 말\\t감정` 만.\n\n" + body)
E = {}
for m in re.finditer(r"^(\d+)\t([^\t]+)\t(\w+)\s*$", out, re.M):
    n, p, t = int(m.group(1)), m.group(2).strip(), m.group(3)
    if 1 <= n <= len(NT) and p in NT[n - 1] and t in ("emotion", "reveal", "twist", "grad_slant", "threat"): E[str(n)] = [p, t]
DY = [d for d in ["그 아기는 나예요", "내 아빠가 아니군요", "넌 코민스키의 손자야", "얼마나 찾았는지 몰라, 아들", "하지만 넌 내 아들이야", "네게 모든 걸 주고 / 희생한 사람이 아빠야", "용서를 구할 사람은 나야", "아니야", "중간 지대요", "내 손으로 제거할 거예요"]
      if any(d in x for x in DT)]
json.dump({"why": "10-27 25 어웨어니스 — 지무비식 자막: 나레 핵심 말 + 감정(agy 고름, 글자 그대로 있는 것만) · 노랑 핵심 대사",
           "n": E, "dlg_yellow": DY}, open(f"{W}/emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("en", len(en), "/", len(NT), "· emph", len(E), "· yellow", len(DY))
