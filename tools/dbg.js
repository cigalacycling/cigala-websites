const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
await p.goto(process.argv[2]+'?x='+Date.now(),{waitUntil:'networkidle'});
const r=await p.evaluate(()=>{const f=document.querySelector('footer');const fb=f?f.getBoundingClientRect().bottom+scrollY:0;
const after=[];document.querySelectorAll('body > *').forEach(e=>{const r=e.getBoundingClientRect();if(r.top+scrollY>=fb-5 && r.height>0) after.push(e.tagName+'.'+e.className+' h'+Math.round(r.height));});
const form=document.querySelector('.cc-form');return {doc:document.documentElement.scrollHeight,fb,after,formW:form&&form.getBoundingClientRect().width,colW:document.querySelector('.cc-formcol')&&document.querySelector('.cc-formcol').getBoundingClientRect().width};});
console.log(JSON.stringify(r));await b.close();})();
