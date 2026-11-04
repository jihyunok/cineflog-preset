# -*- coding: utf-8 -*-
# 24 아포칼립스 Z: 나레 → narr_en.json(영어 뜻, narr_pic 관문용) + emph.json(지무비식 강조: 나레 핵심 말·감정, 노랑 대사) — agy 한 번씩
import json, os, re, subprocess
W = "D:/cine_work/ep24_아포칼립스Z"
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
ns = {}; exec(open(f"{W}/script.py", encoding="utf-8").read(), ns)
NT = [x[1] for x in ns["S"] if x[0] == "N"]
DT = [x[2] for x in ns["S"] if x[0] == "D"]
def ask(p):
    r = subprocess.run([AGY, "-p", p + "\n도구를 쓰지 말고 답해줘.", "--print-timeout", "600s"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout
body = "\n".join(f"{i}\t{t}" for i, t in enumerate(NT, 1))
out = ask("영화 「Apocalypse Z: The Beginning of the End」 리뷰 나레이션이다. 줄마다 자연스러운 영어 한 문장으로 옮겨라(인물: Manel(마넬), his wife Julia(훌리아), sister Belén(벨렌), cat Lúculo(루쿨로), neighbor Gabriela(가브리엘라 할머니), Viktor Pritchenko(프리첸코), captain Ushakov(우샤코프), nurse Lucía(루시아)). 출력은 `번호\\t영어` 만.\n\n" + body)
en = {m.group(1): m.group(2).strip() for m in re.finditer(r"^(\d+)\t(.+)$", out, re.M)}
json.dump(en, open(f"{W}/narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
out = ask("아래 영화 리뷰 나레 줄마다, 화면 자막에서 크게 강조할 핵심 말(그 줄 글 안에 **글자 그대로** 있는 2~12자 토막)과 감정 하나를 골라라. "
          "감정은 emotion(뭉클·슬픔) · reveal(사실이 드러남) · twist(반전·뜻밖) · grad_slant(보통 강조) · threat(불안·위기) 중 하나. 강조할 게 없는 줄은 빼라. "
          "출력은 `번호\\t핵심 말\\t감정` 만.\n\n" + body)
E = {}
for m in re.finditer(r"^(\d+)\t([^\t]+)\t(\w+)\s*$", out, re.M):
    n, p, t = int(m.group(1)), m.group(2).strip(), m.group(3)
    if 1 <= n <= len(NT) and p in NT[n - 1] and t in ("emotion", "reveal", "twist", "grad_slant", "threat"): E[str(n)] = [p, t]
DY = [d for d in ["도와줘요!", "가브리엘라!", "어젯밤엔 아무도 안 왔어, 알겠나?", "아내와 딸이!", "제 아내가 여기서 죽었어요", "미안해, 훌리아", "카나리아 제도로 가는 중이야 / 내가 해냈어, 벨렌", "안 돼! 내 말 들어! / 카나리아에 오지 마", "돌아가! 오지 말고 돌아가!", "우샤코프는 괴물이야"]
      if any(d in x for x in DT)]
json.dump({"why": "10-27 24 아포칼립스 Z — 지무비식 자막: 나레 핵심 말 + 감정(agy 고름, 글자 그대로 있는 것만) · 노랑 핵심 대사",
           "n": E, "dlg_yellow": DY}, open(f"{W}/emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("en", len(en), "/", len(NT), "· emph", len(E), "· yellow", len(DY))
