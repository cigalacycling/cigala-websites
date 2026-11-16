const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();
const pages=fs.readdirSync('.').filter(f=>f.endsWith('.html'));
for(const w of [390,820,1440]){const ctx=await b.newContext({viewport:{width:w,height:900}});
 for(const p of pages){const pg=await ctx.newPage();await pg.goto('http://localhost:8765/'+p,{waitUntil:'load'});await pg.waitForTimeout(400);
  const r=await pg.evaluate(()=>{const sw=document.documentElement.scrollWidth;const wide=[...document.querySelectorAll('body *')].filter(e=>{const b=e.getBoundingClientRect();return b.right>innerWidth+1&&!e.closest('.tbl-wrap')&&getComputedStyle(e).position!=='fixed'}).slice(0,3).map(e=>e.tagName+'.'+e.className);
   return {sw,h1:document.querySelectorAll('h1').length,noalt:[...document.querySelectorAll('img')].filter(i=>!i.getAttribute('alt')).length,
   broken:[...document.querySelectorAll('img')].filter(i=>i.complete&&i.naturalWidth===0).length,
   small:[...document.querySelectorAll('input,textarea,select')].filter(i=>parseFloat(getComputedStyle(i).fontSize)<16).length,wide}});
  const bad=r.sw>w||r.h1!==1||r.noalt||r.small;
  console.log(w,p,JSON.stringify(r),bad?'  <-- CHECK':'');
  if(w!==820){await pg.screenshot({path:`../shots/${p.replace('.html','')}-${w}.png`,fullPage:true});}
  await pg.close();}
 await ctx.close();}
await b.close();})();
