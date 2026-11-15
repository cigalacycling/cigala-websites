const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch(); const dir=process.argv[2];
for (const f of ['index','destinations','destination-lake-garda','guides','guide-lake-como','about','contact']) for (const [n,w] of [['d',1440],['t',820],['p',390]]){
 const p=await b.newPage({viewport:{width:w,height:900}});
 await p.goto('file://'+dir+'/'+f+'.html');
 await p.evaluate(()=>document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')); await p.waitForTimeout(1500);
 const r=await p.evaluate(()=>{const sw=document.documentElement.scrollWidth;const cw=document.documentElement.clientWidth;let bad=[];if(sw>cw){document.querySelectorAll('*').forEach(e=>{const rc=e.getBoundingClientRect();if(rc.right>cw+1&&bad.length<5)bad.push(e.tagName+'.'+e.className)})};return {sw,cw,bad,broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.getAttribute('src')).slice(0,5)}});
 console.log(f,n,r.sw>r.cw?'OVERFLOW '+r.sw+' '+r.bad.join(','):'ok', r.broken.length?'BROKEN '+r.broken.join(','):'');
 await p.screenshot({path:`tpshots/${f}-${n}.png`,fullPage:true}); await p.close();}
await b.close();})();
