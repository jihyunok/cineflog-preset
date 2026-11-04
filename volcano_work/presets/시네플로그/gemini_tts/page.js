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
// ★11-03 크롬이 뒤 탭 타이머를 1분 단위로 묶어(intensive throttling) 묶음 사이 리셋이 10분씩 걸림 → 무음 오디오 시계로 잰다(Worker 는 CSP 로 막힘).
window.__ac = window.__ac || new AudioContext();
window.__acg = window.__acg || (() => { const g = __ac.createGain(); g.gain.value = 0; g.connect(__ac.destination); return g; })();
window.sleep = ms => new Promise(r => { if (__ac.state !== 'running') __ac.resume(); const s = __ac.createConstantSource(); s.connect(__acg); s.onended = () => { s.disconnect(); r(); }; s.start(); s.stop(__ac.currentTime + ms / 1000); });
window.runBtn = () => [...document.querySelectorAll('button')].find(b => /\b(Run|Stop)\b/.test(b.innerText));
window.cineGen = async (text) => {
  const ta = document.querySelector('textarea'); ta.focus();
  Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(ta, text);
  ta.dispatchEvent(new Event('input', {bubbles: true})); ta.dispatchEvent(new Event('change', {bubbles: true}));
  await sleep(1000);
  if (runBtn().getAttribute('aria-disabled') === 'true') return {err: 'run disabled'};
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
// ★11-03 묶음마다 Run 이 꺼지는 문제: 새로고침 대신 화면 안에서 New chat → Create new dialog → Speaker 1 → Ludo (cineReset).
window.cineB = l => [...document.querySelectorAll('button')].find(b => (b.getAttribute('aria-label') || b.innerText || '').includes(l));
window.cineReset = async () => { const nc = cineB('New chat'); if (nc) { nc.click(); await sleep(3000); }
  const c = [...document.querySelectorAll('*')].find(e => e.children.length < 3 && /^Create new dialog$/.test((e.innerText || '').trim())); if (!c) return 'no create';
  c.click(); await sleep(3000); cineB('Speaker 1').click(); await sleep(2000);
  const l = [...document.querySelectorAll('*')].find(e => e.children.length <= 1 && (e.innerText || '').trim() === 'Ludo' && e.getBoundingClientRect().y > 200); if (!l) return 'no ludo';
  l.click(); await sleep(1500);
  const x = [...document.querySelectorAll('button')].find(b => /close/i.test(b.getAttribute('aria-label') || b.innerText || '') && b.getBoundingClientRect().x > 1000); if (x) x.click(); await sleep(1000);
  return (cineB('Speaker 1') || {}).innerText; };
// 자동: recv /next 가 주는 편을 차례로, run disabled 면 cineReset 후 계속. 상태: JSON.stringify([cine.auto, cine.state, cine.log.slice(-4)])
window.cineAuto = async () => { cine.auto = 'on'; let fails = 0;
  while (cine.auto === 'on') { const n = await cineAsk({want: 'next'}, d => d && d.next, 30000).then(d => d.next).catch(() => ({ep: ''}));
    if (!n.ep) { cine.state = 'idle wait ' + new Date().toLocaleTimeString(); await sleep(60000); continue; }
    await cineRun(n.ep);
    if (/^stopped: run disabled/.test(cine.state)) { const r = await cineReset(); cine.log.push('reset ' + r); if (!/Ludo/.test(r)) { cine.auto = 'off: reset ' + r; break; } fails = 0; continue; }
    if (/^stopped/.test(cine.state)) { fails++; cine.log.push('stop#' + fails); if (fails >= 2) { cine.auto = 'off: ' + cine.state; break; } await cineReset(); } else fails = 0; } };
// 시작: await cineReset(); cineAuto();   또는 한 편만 cineRun('epNN_제목')   (recv /next 는 이름순 첫 READY 편을 집으므로 편 이름을 직접 준다)
