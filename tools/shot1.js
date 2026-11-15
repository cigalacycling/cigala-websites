const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:+process.argv[4]||1440,height:900}});
await p.goto(process.argv[2]+'?x='+Date.now(),{waitUntil:'networkidle'});await p.waitForTimeout(1200);
await p.screenshot({path:process.argv[3],fullPage:false,clip:{x:0,y:+process.argv[5]||0,width:+process.argv[4]||1440,height:900}});await b.close();})();
