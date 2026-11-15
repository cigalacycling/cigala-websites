const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();
for (const [n,w] of [['d',1440],['p',390]]){const p=await b.newPage({viewport:{width:w,height:900}});
await p.goto('file://'+process.argv[2]);await p.waitForTimeout(1500);
console.log(n,await p.evaluate(()=>document.documentElement.scrollWidth));
await p.screenshot({path:`look-${n}.png`,fullPage:true});}
await b.close();})();
