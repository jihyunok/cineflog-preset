// AI 스튜디오(aistudio.google.com/generate-speech, 목소리 Ludo) 탭에서 javascript_tool 로 넣는 녹음 루프.
// 계정: 이 PC(시네플로그)는 98 /u/2/ 그대로(10-20 사용자 "2번도 아니고"). 다른 PC 는 10-19 "98계정 사용 안할거야" → 크롬 「진영」 프로필 a93231123.
// ★10-20 다른 PC 에서 이 파일 통째로 바꿈 — 옛 판(cineLoop·audio data: 기다리기)은 git 기록에. ★10-20 새 화면(대작 03): 소리를 아래 재생 막대로 흘려보내고 <audio> 에는 0.04초 빈 파일만 있다 → 옛 「audio data: src 기다리기」는 못 잡는다
//   (게다가 90초 뒤 Run 다시 누르기가 있어 호출을 낭비할 뻔). 새 방식: Run → 버튼이 Stop → Run 으로 돌아오면 「Download」 버튼을 누르되
//   Blob 생성자를 가로채 파일(WAV, 24kHz)을 잡고, 앵커 클릭은 막아 실제 내려받기는 안 한다 → recv 탭으로 postMessage.
// 준비: ① recv.py·splitwatch.py 켜기 ② 편 폴더 READY ③ 이 탭: Create new dialog → 오른쪽 Speaker settings → Ludo 검색·선택 → 닫기
//   ④ 아래 코드 넣고 cineRun('epNN_제목') (모든 묶음을 차례로). 상태: JSON.stringify([cine.state, cine.log.slice(-5)]) — 30~40초마다 봐서 탭을 깨워 둔다.
// ★Run 버튼이 꺼져 있으면(aria-disabled, 10-20 셋째 묶음에서 한 번) 같은 글로 다시 부르지 말고: 페이지 새로고침 → ③ → 이 코드 다시 → cineRun.
// ★실패해도 자동으로 다시 부르지 않는다(사용자 "최대한 절감"). 원인 보고 남은 묶음만 cineRun.
window.rw = window.open('http://127.0.0.1:8771/', 'cinerecv');
window.cine = {log: [], state: 'idle'};
window.cineWait = (pred, ms) => new Promise((res, rej) => { const h = e => { if (pred(e.data)) { removeEventListener('message', h); res(e.data); } }; addEventListener('message', h); if (ms) setTimeout(() => { removeEventListener('message', h); rej(new Error('msg timeout')); }, ms); });
window.cineAsk = (msg, pred, ms) => { const p = cineWait(pred, ms); window.rw.postMessage(msg, '*'); return p; };
if (!window.__OrigBlob) { window.__OrigBlob = window.Blob; window.Blob = function (parts, opts) { const b = new window.__OrigBlob(parts, opts); try { if (b.size > 100000) window.__lastBlob = b; } catch (e) {} return b; }; window.Blob.prototype = window.__OrigBlob.prototype; }
if (!window.__origHEClick) { window.__origHEClick = HTMLElement.prototype.click; HTMLElement.prototype.click = function () { if (this.tagName === 'A' && (this.hasAttribute('download') || /^(blob:|data:)/.test(this.href || ''))) return; return window.__origHEClick.call(this); }; }
if (!window.__origDE) { window.__origDE = EventTarget.prototype.dispatchEvent; EventTarget.prototype.dispatchEvent = function (ev) { if (this instanceof HTMLAnchorElement && ev && ev.type === 'click' && (this.hasAttribute('download') || /^(blob:|data:)/.test(this.href || ''))) return true; return window.__origDE.call(this, ev); }; }
window.__origRDU = window.__origRDU || FileReader.prototype.readAsDataURL;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const runBtn = () => [...document.querySelectorAll('button')].find(b => /\b(Run|Stop)\b/.test(b.innerText));
window.cineGen = async (text) => {
  const ta = document.querySelector('textarea'); ta.focus();
  Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(ta, text);
  ta.dispatchEvent(new Event('input', {bubbles: true})); ta.dispatchEvent(new Event('change', {bubbles: true}));
  await sleep(1000);
  if (runBtn().getAttribute('aria-disabled') === 'true') return {err: 'run disabled — 새로고침 후 다시'};
  const prev = window.__lastBlob; runBtn().click(); cine.log.push('run ' + new Date().toLocaleTimeString());
  let t0 = Date.now();
  while (!/Stop/.test((runBtn() || {}).innerText || '')) { if (Date.now() - t0 > 60000) return {err: 'no start'}; await sleep(500); }
  t0 = Date.now();
  while (/Stop/.test((runBtn() || {}).innerText || '')) { if (Date.now() - t0 > 720000) return {err: 'gen timeout'}; await sleep(2000); }
  await sleep(2500);
  window.__origHEClick.call([...document.querySelectorAll('button')].find(b => b.getAttribute('aria-label') === 'Download'));
  t0 = Date.now(); while (window.__lastBlob === prev) { if (Date.now() - t0 > 30000) return {err: 'no blob'}; await sleep(500); }
  const blob = window.__lastBlob;
  const src = await new Promise(r => { const fr = new FileReader(); fr.onload = () => r(fr.result); window.__origRDU.call(fr, blob); });
  return {src, dur: (blob.size - 44) / 48000};
};
window.cineRun = async (ep) => {
  cine.state = 'jobs ' + ep;
  const j = await cineAsk({want: 'jobs', ep}, d => d && d.jobs && d.ep === ep, 30000);
  cine.log.push(ep + ' jobs ' + j.jobs.length);
  for (const job of j.jobs) {
    cine.state = 'gen ' + job.path; const t0 = Date.now();
    const r = await cineGen(job.text);
    if (r.err) { cine.log.push('FAIL ' + job.path + ' ' + r.err); cine.state = 'stopped: ' + r.err; return; }
    const ack = await cineAsk({path: job.path, b64: r.src}, d => d && d.ok === job.path, 120000);
    cine.log.push(job.path.slice(-22) + ' ' + r.dur.toFixed(1) + 's ' + Math.round((Date.now() - t0) / 1000) + 's ' + ack.n);
    await sleep(1500);
  }
  cine.state = 'done ' + ep;
};
// 시작: cineRun('epNN_제목')   (recv /next 는 이름순 첫 READY 편을 집으므로 편 이름을 직접 준다)
