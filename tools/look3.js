const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();
for (const [n,w] of [['d',1440],['t',820],['p',390]]){const p=await b.newPage({viewport:{width:w,height:900}});
await p.goto('file://'+process.argv[2]);await p.waitForTimeout(1200);
await p.evaluate(()=>document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager'));await p.waitForTimeout(1200);
const sw=await p.evaluate(()=>document.documentElement.scrollWidth); console.log(n,sw>w?'OVERFLOW '+sw:'ok');
await p.screenshot({path:process.argv[3]+'-'+n+'.png',fullPage:true});await p.close();}
await b.close();})();
