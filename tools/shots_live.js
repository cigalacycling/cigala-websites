const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const base=process.argv[2];const out=process.argv[3];
for (const path of ['/','/about/','/contact/','/terms-conditions/']) for (const [n,w] of [['d',1440],['t',820],['p',390]]){
 const p=await b.newPage({viewport:{width:w,height:900}});
 await p.goto(base+path+'?nocache='+Date.now(),{waitUntil:'networkidle',timeout:60000}).catch(e=>console.log('nav',e.message));
 await p.waitForTimeout(1500);
 const r=await p.evaluate(()=>({sw:document.documentElement.scrollWidth,h1:document.querySelectorAll('h1').length,title:document.title}));
 const slug=(path.replace(/\//g,'')||'home'); console.log(slug,n,r.sw>w?'OVERFLOW '+r.sw:'ok','h1',r.h1,r.title);
 await p.screenshot({path:`${out}/${slug}-${n}.png`,fullPage:true}); await p.close();}
await b.close();})();
