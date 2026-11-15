const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900},deviceScaleFactor:2});
for (const f of process.argv.slice(3)){await p.goto('file://'+process.argv[2]+'/'+f);await p.waitForTimeout(600);await p.screenshot({path:process.argv[2]+'/'+f+'.png',clip:{x:400,y:200,width:300,height:200}});}
await b.close();})();
