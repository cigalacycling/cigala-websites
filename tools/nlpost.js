const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext();
  await ctx.route('**/sibforms.com/serve/**', async r => { const q=r.request(); console.log(q.method(), q.headers()['content-type'], (q.postDataBuffer()||Buffer.from('')).toString().replace(/\r\n/g,' | ').slice(0,400)); await r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': 'https://staging.cigalacycling.com' }, body: '{"success":true}' }); });
  const p = await ctx.newPage();
  await p.goto('https://staging.cigalacycling.com/about/?x=' + Date.now(), { waitUntil: 'networkidle' });
  await p.fill('#nl-email-foot', 'test@example.com'); await p.click('.nl-band button[type=submit]'); await p.waitForTimeout(1000);
  console.log(await p.$eval('.nl-band .nl-msg', e => e.textContent));
  await b.close();
})();
