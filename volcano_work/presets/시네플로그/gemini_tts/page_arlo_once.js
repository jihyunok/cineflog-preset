// 10-31 AI 스튜디오 /u/0 Arlo 한 묶음씩: 탭 새로고침(navigate) → 이 코드를 javascript_tool 에 그대로(new Function 은 Trusted Types 로 막힘). 마지막 줄 편 이름만 바꿈. 묶음 하나 끝나면 Run 이 꺼지므로 다시 새로고침→이 코드.
// ★짧게: 코드를 localStorage.cineCode 에 넣어 두고, 새로고침 뒤 → const p=trustedTypes.createPolicy("cine"+Date.now(),{createScript:s=>s}); await (new Function(p.createScript("return (async()=>{"+localStorage.cineCode+"})()")))()
const W=ms=>new Promise(r=>setTimeout(r,ms));
for(let i=0;i<30&&![...document.querySelectorAll('button,a,[role=button]')].some(b=>/Create new dialog/.test(b.innerText));i++) await W(500);
[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='나중에')?.click();
[...document.querySelectorAll('button,a,[role=button]')].find(b=>/Create new dialog/.test(b.innerText))?.click(); await W(3000);
[...document.querySelectorAll('button')].find(b=>/Speaker 1 -/.test(b.innerText)).click(); await W(1500);
const inp=document.querySelector('input[placeholder*="Search"]'); inp.focus(); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(inp,'Arlo'); inp.dispatchEvent(new Event('input',{bubbles:true})); await W(1500);
[...document.querySelectorAll('button')].find(b=>/^\s*Arlo/.test(b.innerText)).click(); await W(1200);
document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true})); await W(800);
const vs=[...document.querySelectorAll('button')].map(b=>b.innerText).find(t=>/Speaker 1 -/.test(t));
if(!/Arlo/.test(vs)) throw new Error('voice '+vs);
window.rw=window.open('','cinerecv');
window.cine = {log: [], state: 'idle'};
window.cineWait = (pred, ms) => new Promise((res, rej) => { const h = e => { if (pred(e.data)) { removeEventListener('message', h); res(e.data); } }; addEventListener('message', h); if (ms) setTimeout(() => { removeEventListener('message', h); rej(new Error('msg timeout')); }, ms); });
window.cineAsk = (msg, pred, ms) => { const p = cineWait(pred, ms); window.rw.postMessage(msg, '*'); return p; };
if (!window.__OrigBlob) { window.__OrigBlob = window.Blob; window.Blob = function (parts, opts) { const b = new window.__OrigBlob(parts, opts); try { if (b.size > 100000) window.__lastBlob = b; } catch (e) {} return b; }; window.Blob.prototype = window.__OrigBlob.prototype; }
if (!window.__origHEClick) { window.__origHEClick = HTMLElement.prototype.click; HTMLElement.prototype.click = function () { if (this.tagName === 'A' && (this.hasAttribute('download') || /^(blob:|data:)/.test(this.href || ''))) return; return window.__origHEClick.call(this); }; }
if (!window.__origDE) { window.__origDE = EventTarget.prototype.dispatchEvent; EventTarget.prototype.dispatchEvent = function (ev) { if (this instanceof HTMLAnchorElement && ev && ev.type === 'click' && (this.hasAttribute('download') || /^(blob:|data:)/.test(this.href || ''))) return true; return window.__origDE.call(this, ev); }; }
window.__origRDU = window.__origRDU || FileReader.prototype.readAsDataURL;
window.sleep = ms => new Promise(r => setTimeout(r, ms));
window.runBtn = () => [...document.querySelectorAll('button')].find(b => /\b(Run|Stop)\b/.test(b.innerText));
window.cineGen = async (text) => {
  const ta = document.querySelector('textarea'); ta.focus();
  Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(ta, text);
  ta.dispatchEvent(new Event('input', {bubbles: true})); ta.dispatchEvent(new Event('change', {bubbles: true}));
  await sleep(1000);
  if (runBtn().getAttribute('aria-disabled') === 'true') return {err: 'run disabled'};
  const prev = window.__lastBlob; runBtn().click(); cine.log.push('run ' + new Date().toLocaleTimeString());
  let t0 = Date.now();
  while (!/Stop/.test((runBtn() || {}).innerText || '')) { if (/quota|exceeded|rate limit/i.test(document.body.innerText)) return {err: 'quota'}; if (Date.now() - t0 > 60000) return {err: 'no start'}; await sleep(500); }
  t0 = Date.now();
  while (/Stop/.test((runBtn() || {}).innerText || '')) { if (Date.now() - t0 > 720000) return {err: 'gen timeout'}; await sleep(2000); }
  await sleep(2500);
  if (/quota|exceeded|rate limit/i.test(document.body.innerText)) return {err: 'quota'};
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
cineRun('ep91r_우아한가'); "go "+vs