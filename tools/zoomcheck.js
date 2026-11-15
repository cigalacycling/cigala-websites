const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ ...devices['iPhone 13'] });
  for (const path of ['/contact/', '/about/']) {
    await p.goto('https://staging.cigalacycling.com' + path + '?x=' + Date.now(), { waitUntil: 'networkidle' });
    console.log(path, JSON.stringify(await p.$$eval('input:not([type=hidden]):not(.nl-hp), textarea, select', els => els.filter(e => e.offsetParent).map(e => (e.name || e.id) + ':' + getComputedStyle(e).fontSize))));
  }
  await b.close();
})();
