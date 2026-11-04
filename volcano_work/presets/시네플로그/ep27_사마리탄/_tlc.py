# -*- coding: utf-8 -*-
"""_tl.txt → _tlc.txt (컷 설명은 12초에 하나, 같은 자막 대사 줄은 id 묶음) — 대본 쓰기용 짧은 시간표. 10-28"""
import re
out = []; last = ""; lastshot = -99
for r in open("_tl.txt", encoding="utf-8"):
    r = r.rstrip()
    if r.startswith("##"):
        t = float(r.split()[1])
        if t - lastshot >= 12:
            d = re.sub(r"^(In|On|At) ([^,]*), ", r"[\2] ", r[3:].split(" ", 1)[1]); out.append(f"## {t:.0f} {d[:80]}"); lastshot = t
    else:
        i, t, k = r.split(" ", 2)
        if k == last: out[-1] = out[-1].split(" ", 1)[0] + "," + i.rstrip("✗") + " " + out[-1].split(" ", 1)[1]; continue
        last = k; out.append(f"{i} {float(t):.0f} {k}")
open("_tlc.txt", "w", encoding="utf-8").write("\n".join(out) + "\n"); print(len(out))
