const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();
for (const f of ['index','about','contact','terms']) for (const [n,w] of [['d',1440],['t',820],['p',390]]){const p=await b.newPage({viewport:{width:w,height:900}});
await p.goto('file://'+process.argv[2]+'/'+f+'.html');await p.waitForTimeout(800);
const sw=await p.evaluate(()=>document.documentElement.scrollWidth);
console.log(f,n,sw>w?'OVERFLOW '+sw:'ok');
await p.screenshot({path:`lk-${f}-${n}.png`,fullPage:true});await p.close();}
await b.close();})();
