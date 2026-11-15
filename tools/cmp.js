const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:812},deviceScaleFactor:2});
for (const o of ['svg','png']){await p.goto('file://'+process.argv[2]+'/cmp-'+o+'.html');await p.waitForTimeout(800);
await p.screenshot({path:`cmp-${o}.png`,clip:{x:540,y:280,width:280,height:180}});}
await b.close();})();
