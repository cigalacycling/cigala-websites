const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();
const pages=fs.readdirSync('.').filter(f=>f.endsWith('.html'));
for(const w of [390,1440]){const ctx=await b.newContext({viewport:{width:w,height:900}});
 for(const p of pages){const pg=await ctx.newPage();await pg.goto('http://localhost:8765/'+p,{waitUntil:'load'});
  const H=await pg.evaluate(()=>document.body.scrollHeight);for(let y=0;y<H;y+=600){await pg.evaluate(y=>scrollTo(0,y),y);await pg.waitForTimeout(60);}
  await pg.evaluate(()=>scrollTo(0,0));await pg.waitForTimeout(500);
  const broken=await pg.evaluate(()=>[...document.images].filter(i=>!i.complete||i.naturalWidth===0).length);
  if(broken)console.log('NOT LOADED',w,p,broken);
  await pg.screenshot({path:`../shots/${p.replace('.html','')}-${w}.png`,fullPage:true});await pg.close();}
 await ctx.close();}
await b.close();})();
