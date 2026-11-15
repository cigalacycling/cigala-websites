const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } }); const p = await (await b.newContext()).newPage();
  const u = 'https://staging.tours.cigalacycling.com/';
  const dl = () => p.evaluate(() => dataLayer.map(a => { const x = [...a]; return x[0] + ':' + (typeof x[1] === 'string' ? x[1] : x[1] && x[1].analytics_storage || ''); }));
  for (let i=0;i<20;i++){try{const r=await p.goto(u + '?x=' + Date.now(), { waitUntil: 'domcontentloaded', timeout: 60000 }); if(r&&r.status()<500) break;}catch(e){} await p.waitForTimeout(3000);} await p.waitForTimeout(1500);
  console.log('new visitor:', await dl());
  await p.click('#cc-consent .cc-accept');
  console.log('after accept:', await dl());
  for (let i=0;i<20;i++){try{const r=await p.goto(u + 'trips/?x=' + Date.now(), { waitUntil: 'domcontentloaded', timeout: 60000 }); if(r&&r.status()<500) break;}catch(e){} await p.waitForTimeout(3000);} await p.waitForTimeout(1500);
  console.log('returning:', await dl(), 'ga-disable:', await p.evaluate(() => window['ga-disable-G-QRF16ZZVDB']));
  await b.close();
})();
