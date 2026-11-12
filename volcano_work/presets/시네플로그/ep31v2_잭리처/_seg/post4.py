# -*- coding: utf-8 -*-
"""post3.py 뒤(11-12 31v2) — cold_read(agy 안 본 시청자) 후보 중 고칠 4줄. 나머지는 ep.json cold_ok 에 줄마다 이유.
판단 근거: 녹음 문장 길이(narr/nNNN.json) + 앞뒤 조각 3초 간격(windows.json) + 컷 설명(room.py)·프레임(_seg/s_k3.jpg)."""
import json
WK = r"D:\cine_work\ep31v2_잭리처"
R = [  # (옛 줄 앞부분 그대로, 새 줄, 새 EN 또는 None)
 ('("N", "혼수상태로 병상에 누운 바. 리처는 왜 그를 보호하지 않았냐고 따지죠.", [(727.2, 734.3), (735.4, 738.6)], {"sent": True}',
  '("N", "수감자들에게 맞아 혼수상태가 된 바. 리처는 왜 그를 보호하지 않았냐고 따지죠.", [(727.2, 734.3), (735.4, 738.6)], {"sent": True, "result_ok": "이미 혼수상태로 누운 바의 병상 컷(727) 위 — 맞은 건 화면 앞의 지난 일을 꾸미는 말, 뒤 대사 「늑대 소굴에 처넣다니」는 리처가 같은 사실을 따지는 말(새 사건을 앞질러 알리지 않음)"}',
  "Barr lies in a coma after being beaten by inmates. Reacher demands to know why he wasn't protected."),   # cold [원인] 왜 혼수상태인지 — 지난 일 꾸밈말(프레임 봄 s_k459.jpg 727.6 병상의 바·로딘·리처)
 ('("N", "그날 밤 모텔 방, 리처는 하나뿐인 셔츠를 빨고 있죠. 헬렌도 와 있죠."',
  '("N", "그날 밤 모텔 방, 풀려난 리처는 하나뿐인 셔츠를 빨고 있죠. 헬렌도 와 있죠."',
  "That night at the motel, the released Reacher washes his only shirt. Helen is there too."),   # cold [장소] 유치장에서 어떻게 — 앞 대사 「아무도 고소를 않잖소」 + 꾸밈말 「풀려난」(프레임 봄 2485 모텔 밖·2490.3 세면대 셔츠·2495.3 앉은 헬렌)
 ('("N", "리처도 총을 내려놓습니다. 두 사람은 맨주먹으로 맞붙죠.", [(6877.0, 6880.1), (6893.8, 6897.7)]',
  '("N", "빈손의 찰리 앞에서, 리처도 총을 내려놓습니다. 두 사람은 맨주먹으로 맞붙죠.", [[(6871.8, 6874.9), (6876.0, 6880.0)], (6893.8, 6897.7)]',
  "Facing an empty-handed Charlie, Reacher lowers his gun too. The two fight with bare fists."),   # cold [뜬금] 「리처도」 — 프레임 봄 s_418.jpg: 6871.8~6874.8 빈손으로 선 찰리(앞쪽 리처 어깨) · 6875.5~6879.2 소총을 든 리처가 내려 던짐 (6865~6871 은 멀리 작은 두 사람이라 안 씀)
 ('("N", "안으로 들어서며 총구를 겨누는 리처. 헬렌은 아버지를 의심했던 걸 후회하죠.", [(7055.0, 7064.3), (7068.0, 7076.4)], {"sent": True}',
  '("N", "안으로 들어서며 총구를 겨누는 리처. 총구는 여전히 헬렌을 노리고 있죠.", [(7055.0, 7064.3), (7072.5, 7076.3)], {"sent": True}',
  "Reacher steps inside with his rifle raised. A gun is still pointed at Helen."),   # cold [원인] — ★옛 글 「헬렌은 아버지를 의심했던 걸 후회하죠」는 대사 7079 「아버지 일은 내가 틀렸나요?」(묻는 말)와 다름. 프레임 봄 s_425b.jpg: 7065~7076 은 쓰러지는 에머슨이 아니라(컷 설명 오인) 의자의 헬렌 가슴께로 들이댄 권총 · 앞쪽 가죽 재킷 남자
]
s = open(f"{WK}/script.py", encoding="utf-8").read()
en = json.load(open(f"{WK}/narr_en.json", encoding="utf-8")); em = json.load(open(f"{WK}/emph.json", encoding="utf-8"))
ns0 = {}; exec(s, ns0); T0 = [x[1] for x in ns0["S"] if x[0] == "N"]
t2e = {t: en.get(str(i + 1), "") for i, t in enumerate(T0)}; t2m = {t: em["n"].get(str(i + 1)) for i, t in enumerate(T0)}
for a, b, e in R:
    assert s.count(a) == 1, a[:50]
    s = s.replace(a, b)
ns = {}; exec(s, ns); NT = [x[1] for x in ns["S"] if x[0] == "N"]
for (t_old, t_new) in zip(T0, NT):
    if t_old != t_new:
        e = next((e for a, b, e in R if t_new in b), None)
        t2e[t_new] = e or t2e.get(t_old, ""); t2m[t_new] = t2m.get(t_old)
open(f"{WK}/script.py", "w", encoding="utf-8").write(s)
json.dump({str(i + 1): t2e.get(t, "") for i, t in enumerate(NT)}, open(f"{WK}/narr_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
em["n"] = {str(i + 1): t2m[t] for i, t in enumerate(NT) if t2m.get(t) and t2m[t][0] in t}
json.dump(em, open(f"{WK}/emph.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", len(NT), "· 바뀐 글", sum(a != b for a, b in zip(T0, NT)), "· 영어 없음", [t[:20] for t in NT if not t2e.get(t)], "· 강조", len(em["n"]))
