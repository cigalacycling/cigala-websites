// Tours STAGING layout check (CLAUDE.md): 390/820/1440 wide, no sideways scroll, one H1, form fields 16px,
// every <img> with alt text. Optional full-page screenshots at 390 and 1440 into a folder.
// Usage: node tools/layout_check_tours.js /about/ /contact/ [--shots /path/to/folder]
const {chromium} = require('playwright');
(async () => {
  const args = process.argv.slice(2); const si = args.indexOf('--shots');
  const shots = si >= 0 ? args.splice(si, 2)[1] : null; let bad = 0;
  const b = await chromium.launch();
  for (const u of args) for (const w of [390, 820, 1440]) {
    const p = await b.newPage({viewport: {width: w, height: 900}});
    for (let k = 0; k < 6; k++) { const r = await p.goto('https://staging.tours.cigalacycling.com' + u + '?v=' + Date.now(), {waitUntil: 'load', timeout: 90000}).catch(() => null); if (r && r.status() == 200) break; await p.waitForTimeout(3000); }
    const d = await p.evaluate(() => {
      const wide = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.right > innerWidth + 1 && getComputedStyle(e).position != 'fixed'; }).slice(0, 3).map(e => e.tagName + '.' + (e.className || '').toString().slice(0, 40));
      const small = [...document.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]), select, textarea')].filter(e => e.offsetParent && parseFloat(getComputedStyle(e).fontSize) < 16).length;
      const noalt = [...document.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).map(i => i.src.slice(-50));
      return {sw: document.documentElement.scrollWidth, h1: document.querySelectorAll('h1').length, small, noalt, wide};
    });
    const ok = d.sw <= w && d.h1 == 1 && !d.small && !d.noalt.length;
    if (!ok) bad++;
    console.log(ok ? 'OK ' : 'BAD', u, w, JSON.stringify(d));
    if (shots && w != 820) {
      await p.evaluate(() => { document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager'); document.querySelectorAll('[class*=consent],.cc-banner').forEach(e => e.style.display = 'none'); });
      for (let y = 0; y < await p.evaluate(() => document.body.scrollHeight); y += 700) { await p.evaluate(v => scrollTo(0, v), y); await p.waitForTimeout(120); }
      await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(2500);
      await p.screenshot({path: `${shots}/${u.replace(/\//g, '_')}${w}.png`, fullPage: true});
    }
    await p.close();
  }
  await b.close(); process.exit(bad ? 1 : 0);
})();
