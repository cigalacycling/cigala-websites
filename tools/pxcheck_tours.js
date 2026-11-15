const { chromium } = require('playwright');
async function go(p, u) { for (let i = 0; i < 20; i++) { try { const r = await p.goto(u, { waitUntil: 'load', timeout: 60000 }); if (r && r.status() < 500) return; } catch (e) {} await p.waitForTimeout(3000); } }
(async () => {
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  for (const choice of ['accept', 'reject']) {
    const p = await (await b.newContext()).newPage();
    const fb = []; p.on('request', r => { if (/facebook\.(net|com)/.test(r.url())) fb.push(r.url().slice(0, 70)); });
    await go(p, 'https://staging.tours.cigalacycling.com/?x=' + Date.now()); await p.waitForTimeout(3000);
    const before = { fbq: await p.evaluate(() => typeof window.fbq), requests: fb.length };
    await p.click('#cc-consent .cc-' + choice); await p.waitForTimeout(3000);
    const after = await p.evaluate(() => ({ fbq: typeof window.fbq, queue: window.fbq && window.fbq.queue ? window.fbq.queue.map(a => Array.from(a).join(' ')) : null, stored: localStorage.getItem('cc_consent') }));
    console.log(choice.toUpperCase(), '| before:', JSON.stringify(before), '| after:', JSON.stringify(after), '| facebook requests:', fb.join(' ') || 'none');
    await p.close();
  }
  await b.close();
})();
