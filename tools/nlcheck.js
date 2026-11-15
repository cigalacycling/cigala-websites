const { chromium } = require('playwright');
const BASE = 'https://staging.cigalacycling.com';
(async () => {
  const b = await chromium.launch();
  for (const w of [390, 1440]) {
    const ctx = await b.newContext({ viewport: { width: w, height: w === 390 ? 844 : 900 } });
    let posted = null;
    await ctx.route('**/sibforms.com/serve/**', async r => { posted = r.request().postData(); await r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': BASE }, body: '{"success":true}' }); });
    const p = await ctx.newPage();
    // 1) fresh visitor: no pop-up while cookie banner is up
    await p.goto(BASE + '/?x=' + Date.now(), { waitUntil: 'networkidle' });
    await p.evaluate(() => sessionStorage.setItem('cc_nl_t0', Date.now() - 60000));
    await p.reload({ waitUntil: 'networkidle' }); await p.waitForTimeout(2500);
    console.log(w, 'banner up -> popup hidden:', await p.$eval('#nl-pop', e => e.hidden));
    // 2) after consent choice -> pop-up shows
    await p.click('#cc-consent .cc-reject'); await p.waitForTimeout(2500);
    console.log(w, 'after reject -> popup hidden:', await p.$eval('#nl-pop', e => e.hidden));
    await p.screenshot({ path: `wp/shots/nl-pop-${w}.png` });
    // invalid email
    await p.fill('#nl-email-pop', 'abc'); await p.click('#nl-pop button[type=submit]');
    console.log(w, 'invalid msg:', await p.$eval('#nl-pop .nl-msg', e => e.textContent));
    await p.fill('#nl-email-pop', 'test@example.com'); await p.click('#nl-pop button[type=submit]'); await p.waitForTimeout(800);
    console.log(w, 'ok msg:', await p.$eval('#nl-pop .nl-msg', e => e.textContent), 'posted EMAIL:', /test@example\.com/.test(posted || ''));
    await p.screenshot({ path: `wp/shots/nl-pop-done-${w}.png` });
    await p.waitForTimeout(4000);
    console.log(w, 'auto-closed:', await p.$eval('#nl-pop', e => e.hidden), 'state:', await p.evaluate(() => localStorage.getItem('cc_nl')));
    // footer band screenshot (fresh state)
    await p.evaluate(() => localStorage.removeItem('cc_nl'));
    await p.goto(BASE + '/about/?x=' + Date.now(), { waitUntil: 'networkidle' });
    await p.evaluate(() => { const n = document.getElementById('nl-pop'); n.remove(); });
    const f = await p.$('footer footer'); await f.scrollIntoViewIfNeeded(); await p.waitForTimeout(400);
    await f.screenshot({ path: `wp/shots/nl-foot-${w}.png` });
    console.log(w, 'overflow:', await p.evaluate(() => document.documentElement.scrollWidth > innerWidth), 'headings in footer:', await p.$$eval('footer footer h1, footer footer h2, footer footer h3', e => e.length));
    // close + snooze
    await p.evaluate(() => { localStorage.removeItem('cc_nl'); sessionStorage.setItem('cc_nl_t0', Date.now() - 60000); });
    await p.goto(BASE + '/terms-conditions/?x=' + Date.now(), { waitUntil: 'networkidle' }); await p.waitForTimeout(2500);
    console.log(w, 'terms popup shown:', !(await p.$eval('#nl-pop', e => e.hidden)));
    await p.keyboard.press('Escape');
    console.log(w, 'esc closed:', await p.$eval('#nl-pop', e => e.hidden), 'snoozed:', /"c"/.test(await p.evaluate(() => localStorage.getItem('cc_nl'))));
    await p.goto(BASE + '/?x=' + Date.now(), { waitUntil: 'networkidle' }); await p.waitForTimeout(2500);
    console.log(w, 'after close, next page hidden:', await p.$eval('#nl-pop', e => e.hidden));
    // contact page never
    await p.evaluate(() => localStorage.removeItem('cc_nl'));
    await p.goto(BASE + '/contact/?x=' + Date.now(), { waitUntil: 'networkidle' }); await p.waitForTimeout(2500);
    console.log(w, 'contact hidden:', await p.$eval('#nl-pop', e => e.hidden));
    await ctx.close();
  }
  await b.close();
})();
