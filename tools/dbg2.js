const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
await p.goto('https://staging.cigalacycling.com/about/?x='+Date.now(),{waitUntil:'networkidle'});await p.waitForTimeout(4000);
const r=await p.evaluate(()=>({cur:[...document.querySelectorAll('.menu a[aria-current]')].map(a=>a.textContent+' '+getComputedStyle(a).boxShadow),ow:!!window.OpenWidget,owScript:!![...document.scripts].find(s=>s.src.includes('openwidget')),cookie:!!document.getElementById('cookie-consent')}));
console.log(JSON.stringify(r));await p.screenshot({path:'wp/shots/about-top.png',clip:{x:0,y:0,width:1440,height:120}});await b.close();})();
