const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext(); const hits = [];
  await ctx.route(/google-analytics\.com\/g\/collect|googletagmanager\.com/, async r => { const u = r.request().url(); if (u.includes('/collect')) { hits.push(new URL(u).searchParams.get('gcs') + ' ' + new URL(u).searchParams.get('en')); return r.fulfill({ status: 204, body: '' }); } return r.continue(); });
  const p = await ctx.newPage();
  const u = 'https://staging.cigalacycling.com/';
  await p.goto(u + '?x=' + Date.now(), { waitUntil: 'networkidle' }); await p.waitForTimeout(1500);
  console.log('new visitor hits (gcs en):', hits.splice(0));
  await p.click('#cc-consent .cc-accept'); await p.waitForTimeout(2000);
  console.log('after accept:', hits.splice(0));
  await p.goto(u + 'about/?x=' + Date.now(), { waitUntil: 'networkidle' }); await p.waitForTimeout(2000);
  console.log('returning accepted visitor:', hits.splice(0));
  await b.close();
})();
