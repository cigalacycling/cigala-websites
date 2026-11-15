const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();
for (const [n,w,h] of [['big',3240,5760],['small',1080,1920]]){const p=await b.newPage({viewport:{width:w,height:h}});
await p.goto('file://'+process.argv[2]+'/'+n+'.html');await p.waitForTimeout(800);await p.screenshot({path:process.argv[2]+'/'+n+'.png'});await p.close();}
await b.close();})();
