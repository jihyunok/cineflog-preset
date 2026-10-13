# AI 스튜디오(Gemini TTS) 음성을 받아 D:/cine_work 아래에 저장하는 수신기 (port 8771)
# GET /        = 받는 페이지(aistudio 가 window.open 으로 열고 postMessage 로 주고받음)
# GET /jobs?ep=ep14_더픽업 = 아직 안 만든 묶음 [{path, text}] (epNN/batches.json → epNN/gem/bKK_n0_n1.wav)
# POST /       = {path, b64} 저장
import base64, json, os, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ROOT = os.environ.get("CINE_WORK") or ("D:/cine_work" if os.path.isdir("D:/") else os.path.expanduser("~/cine_work"))
PAGE = """<!doctype html><meta charset=utf-8><title>recv</title><pre id=l>ready</pre><script>
window.__log = [];
addEventListener('message', async e => { const d = e.data; if (!d) return;
  try {
    if (d.want === 'next') { const j = await (await fetch('/next')).json(); e.source.postMessage({next: j}, '*'); return; }
    if (d.want === 'jobs') { const j = await (await fetch('/jobs?ep=' + encodeURIComponent(d.ep))).json(); e.source.postMessage({jobs: j, ep: d.ep}, '*'); return; }
    if (!d.path) return;
    const r = await fetch('/', {method: 'POST', body: JSON.stringify(d)}); const t = await r.text();
    window.__log.push(d.path + ' ' + t); e.source.postMessage({ok: d.path, n: t}, '*');
  } catch (err) { window.__log.push('ERR ' + err.message); }
});
</script>""".encode("utf-8")
def jobs(ep):
    if not os.path.exists(f"{ROOT}/{ep}/batches.json"): return []
    b = json.load(open(f"{ROOT}/{ep}/batches.json", encoding="utf-8"))
    out = []
    for k, (n0, n1, t) in enumerate(b):
        p = f"{ep}/gem/b{k:02d}_{n0:04d}_{n1:04d}.wav"
        if not os.path.exists(f"{ROOT}/{p}"): out.append({"path": p, "text": t})
    return out
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/next":
            eps = sorted(d for d in os.listdir(ROOT) if d.startswith("ep") and os.path.isdir(f"{ROOT}/{d}"))
            nxt = next((e for e in eps if os.path.exists(f"{ROOT}/{e}/READY") and jobs(e)), "")
            alld = all(os.path.exists(f"{ROOT}/{e}/READY") and not jobs(e) for e in eps)
            body = json.dumps({"ep": nxt, "all": alld}, ensure_ascii=False).encode("utf-8"); ct = "application/json; charset=utf-8"
        elif u.path == "/jobs":
            ep = urllib.parse.parse_qs(u.query)["ep"][0]
            body = json.dumps(jobs(ep), ensure_ascii=False).encode("utf-8"); ct = "application/json; charset=utf-8"
        else: body = PAGE; ct = "text/html; charset=utf-8"
        self.send_response(200); self.send_header("Content-Type", ct); self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        p = os.path.normpath(os.path.join(ROOT, d["path"]))
        assert p.startswith(os.path.normpath(ROOT))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        b = base64.b64decode(d["b64"].split(",", 1)[-1]); open(p + ".part", "wb").write(b); os.replace(p + ".part", p)
        print("saved", p, len(b), flush=True)
        self.send_response(200); self.end_headers(); self.wfile.write(str(len(b)).encode())
ThreadingHTTPServer(("127.0.0.1", 8771), H).serve_forever()
