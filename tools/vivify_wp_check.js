// Check every Vivify page on the WordPress draft at 390/820/1440: sideways scroll, one H1, alt text, broken images, form font size.
const {chromium}=require('playwright');const fs=require('fs');
const S='https://basic-darkslategray-cod-55.hostingersite.com';
const pages=process.argv.slice(2).length?process.argv.slice(2):Object.keys(JSON.parse(fs.readFileSync(__dirname+'/../vivify/wp-pages.json'))).map(f=>f==='index.html'?'home':f.slice(0,-5));
(async()=>{const b=await chromium.launch();let bad=0;
for(const w of [390,820,1440]){const ctx=await b.newContext({viewport:{width:w,height:900}});
 for(const p of pages){const pg=await ctx.newPage();
  try{await pg.goto(`${S}/${p}/`,{waitUntil:'networkidle',timeout:90000});}catch(e){console.log('TIMEOUT',p);}
  const H=await pg.evaluate(()=>document.body.scrollHeight);for(let y=0;y<H;y+=900){await pg.evaluate(y=>scrollTo(0,y),y);await pg.waitForTimeout(40);}
  await pg.waitForTimeout(300);
  const r=await pg.evaluate(()=>({sw:document.documentElement.scrollWidth,h1:document.querySelectorAll('h1').length,
   noalt:[...document.images].filter(i=>!i.hasAttribute('alt')||(!i.alt&&!i.closest('[aria-hidden]'))).map(i=>i.src.split('/').pop()).slice(0,3),
   broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0&&!i.src.includes('s.w.org/images/core/emoji')&&!i.src.includes('cdn.trustindex.io')&&!i.src.includes('googleusercontent.com')).map(i=>i.src.split('/').pop()).slice(0,3),
   small:[...document.querySelectorAll('input:not([type=checkbox]):not([type=hidden]):not([type=submit]),textarea,select')].filter(i=>parseFloat(getComputedStyle(i).fontSize)<16).length}));
  if(r.sw>w||r.h1!==1||r.noalt.length||r.broken.length||r.small){bad++;console.log(w,p,JSON.stringify(r));}
  await pg.close();}
 await ctx.close();}
console.log(pages.length*3,'checks, problems:',bad);await b.close();})();
