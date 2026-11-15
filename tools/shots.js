const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const urls = process.argv.slice(2);
  const sizes = {phone:[390,844],tablet:[820,1180],desktop:[1440,900]};
  for (const u of urls) for (const [n,[w,h]] of Object.entries(sizes)) {
    const p = await b.newPage({viewport:{width:w,height:h}});
    await p.goto(u,{waitUntil:'networkidle',timeout:60000}).catch(e=>console.log('nav',e.message));
    await p.waitForTimeout(1500);
    const r = await p.evaluate(()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,bg:[...document.querySelectorAll('*')].filter(e=>/url\(/.test(getComputedStyle(e).backgroundImage)).length}));
    const slug=(new URL(u).pathname.replace(/\//g,'')||'home');
    await p.screenshot({path:`shots/${slug}-${n}.png`,fullPage:true});
    console.log(slug,n,'scrollW',r.sw,'clientW',r.cw,r.sw>r.cw?'HORIZONTAL SCROLL':'ok','cssBgImages',r.bg);
    await p.close();
  }
  await b.close();
})();
