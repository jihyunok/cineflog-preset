// AI 스튜디오(aistudio.google.com/u/2/generate-speech, 목소리 Ludo) 탭에서 javascript_tool 로 넣는 녹음 루프.
// 1) window.rw = window.open('http://127.0.0.1:8771/','cinerecv')  (크롬 다중 다운로드·로컬망 fetch 가 막혀서 recv 탭에 postMessage)
// 2) 2026-10-07 세션의 cineGen / cineRun / cineLoop 정의 → window.cineLoop()
//    cineLoop: recv /next 로 READY 편을 받아 batches.json 묶음마다 textarea 채우고 Run → audio data: 가 생기고 Run 버튼이 돌아오면 recv 로 보냄
// ★크롬 창이 숨겨지면 페이지 타이머가 멈춘다 → 3분마다 computer screenshot 으로 깨운다(beat.sh 로 메인을 깨움).

// ── 아래가 2026-10-07 실제로 돌린 코드 (대화 기록에서 복원, 10-09) ──
// 그 전에 한 번: window.rw = window.open('http://127.0.0.1:8771/','cinerecv')  (recv.py 를 먼저 켠다)
window.cine = window.cine || {log: [], state: 'idle'};
window.cineWait = (pred, ms) => new Promise((res, rej) => { const h = e => { if (pred(e.data)) { removeEventListener('message', h); res(e.data); } }; addEventListener('message', h); if (ms) setTimeout(() => { removeEventListener('message', h); rej(new Error('msg timeout')); }, ms); });
if (window.cineIv) clearInterval(window.cineIv);
window.cineGen = (text) => new Promise((res) => {
  const ta = document.querySelector('textarea');
  Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(ta, text);
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  const old = (document.querySelector('audio') || {}).src || '';
  const need = text.length / 410 * 60 * 0.5;
  const btn = () => [...document.querySelectorAll('button')].find(b => /^(Run|Stop)/.test(b.innerText.trim()));
  let done = false, clicked = false, t0 = Date.now();
  const check = () => { if (done || !clicked) return; const a = document.querySelector('audio'); const b = btn(); const bt = b ? b.innerText.trim() : '';
    if (a && a.src && a.src !== old && a.src.startsWith('data:') && a.duration > need && bt.startsWith('Run')) { done = true; clearInterval(iv); res({src: a.src, dur: a.duration}); }
    else if (Date.now() - t0 > 90000 && bt.startsWith('Run') && !(a && a.src !== old)) { // 눌렀는데 시작 안 됨 → 다시 누름
      t0 = Date.now(); cine.log.push('reclick'); b.click(); } };
  const iv = setInterval(check, 4000);
  setTimeout(() => { btn().click(); clicked = true; t0 = Date.now(); }, 800);
  setTimeout(() => { if (!done) { done = true; clearInterval(iv); res({err: 'timeout', body: document.body.innerText.slice(-300)}); } }, 900000);
});
window.cineAsk = (msg, pred, ms) => { const p = cineWait(pred, ms); window.rw.postMessage(msg, '*'); return p; };
window.cineLoop = async () => {
  let fails = 0;
  while (true) {
    try {
      const n = (await cineAsk({want: 'next'}, d => d && d.next, 30000)).next;
      if (n.all) { cine.state = 'ALL DONE'; return; }
      if (!n.ep) { cine.state = 'waiting READY'; await new Promise(r => setTimeout(r, 60000)); continue; }
      await cineRun(n.ep); fails = 0;
      if (cine.state.startsWith('failed')) throw new Error(cine.state);
    } catch (e) { fails++; cine.log.push('loop err ' + e.message); cine.state = 'retrywait'; await new Promise(r => setTimeout(r, Math.min(600000, 60000 * fails))); }
  }
};
window.cineRun = async (ep) => {
  cine.state = 'jobs ' + ep;
  const j = await cineAsk({want: 'jobs', ep}, d => d && d.jobs && d.ep === ep, 30000);
  cine.log.push(ep + ' jobs ' + j.jobs.length);
  for (const job of j.jobs) {
    cine.state = 'gen ' + job.path; const t0 = Date.now();
    const r = await cineGen(job.text);
    if (r.err) { cine.log.push('FAIL ' + job.path + ' ' + r.err + ' ' + r.body); cine.state = 'failed'; return; }
    const ack = await cineAsk({path: job.path, b64: r.src}, d => d && d.ok === job.path, 120000);
    cine.log.push(job.path + ' ' + r.dur.toFixed(1) + 's ' + Math.round((Date.now() - t0) / 1000) + 's ' + ack.n);
    await new Promise(r => setTimeout(r, 1500));
  }
  cine.state = 'done ' + ep;
};
// 시작: if (!window.cineLoopOn) { window.cineLoopOn = true; window.cineLoop(); }
// 상태 보기: JSON.stringify([cine.state, cine.log.slice(-5)])
