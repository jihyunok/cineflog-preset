// ★10-27 새벽(dr05) AI 스튜디오 새로고침 뒤 「새 대화 → Ludo → 패널 닫기」를 javascript_tool 한 번으로(화면 클릭·스크린샷이 굳을 때도 됨).
// 순서: navigate(새로고침) → 이 코드 → page_inline.js 본문 붙여 넣기 → setTimeout(()=>cineRun('dr05_검은태양/partN'), 4000)
// ★패널(Speaker settings)을 안 닫으면 Run 을 눌러도 시작 안 함(no start) — 「패널 닫기」 버튼 꼭 누름.
const sl = ms => new Promise(r => setTimeout(r, ms));
for (let i = 0; i < 30 && !(document.body && (/Create new dialog/.test(document.body.innerText) || [...document.querySelectorAll("button")].some(b => /Speaker 1 - /.test(b.innerText)))); i++) await sl(1000);  // 11-08 모델 = gemini-3.8-flash-lite-tts
const leaf = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && (e.innerText || e.textContent || '').trim() === 'Create new dialog');
let el = leaf; while (el && !(el.tagName === 'BUTTON' || el.tagName === 'MAT-CARD' || el.getAttribute('role') === 'button')) el = el.parentElement;
(el || leaf).click(); await sl(3000);
[...document.querySelectorAll('button')].find(b => /Speaker 1 - /.test(b.innerText)).click(); await sl(2500);
const inp = document.querySelector('input[placeholder*="Search"]');
if (inp) { inp.focus(); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(inp, 'Ludo'); inp.dispatchEvent(new Event('input', {bubbles: true})); await sl(2500); }
const b = [...document.querySelectorAll('button')].find(b => /^Ludo\n/.test(b.innerText)); if (b) b.click(); await sl(2500);
const cl = [...document.querySelectorAll('button')].find(b => (b.getAttribute('aria-label') || '') === '패널 닫기' || (b.getAttribute('aria-label') || '') === 'Close panel'); if (cl) cl.click(); await sl(1000);
[!!inp, !!b, !!cl, [...document.querySelectorAll('button')].some(b => /Speaker 1 - Ludo/.test(b.innerText))]
