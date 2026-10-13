import numpy as np, json
M = np.load("masks.npy"); FPS = 5
B = np.unpackbits(M, axis=1).astype(bool)
cnt = B.sum(1)
on = cnt > 60
ev = []; cur = None
def iou(a, b):
    u = (a | b).sum(); return (a & b).sum() / u if u else 1
for k in range(len(B)):
    if not on[k]:
        if cur: ev.append(cur); cur = None
        continue
    if cur and iou(B[k], B[cur["ref"]]) > 0.45: cur["e"] = k; continue
    if cur: ev.append(cur)
    cur = {"s": k, "e": k, "ref": k}
if cur: ev.append(cur)
out = [{"id": i + 1, "s": round(e["s"] / FPS, 2), "e": round((e["e"] + 1) / FPS, 2), "f": e["ref"] + (e["e"] - e["s"]) // 2} for i, e in enumerate(ev) if e["e"] - e["s"] >= 2]
for i, e in enumerate(out): e["id"] = i + 1
json.dump(out, open("subev.json", "w"), indent=0)
print("events", len(out), "median len", np.median([e["e"] - e["s"] for e in out]))
