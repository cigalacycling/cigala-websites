const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();
for (const w of [390,1440]){const p=await b.newPage({viewport:{width:w,height:900}});
await p.goto('https://staging.cigalacycling.com/about/?x='+Date.now(),{waitUntil:'networkidle'});
const r=await p.evaluate(()=>{const f=document.querySelector('footer[data-elementor-type="footer"]');const inner=f.querySelector('footer');const prev=f.previousElementSibling;let last=document.querySelector('main, .elementor-location-single, [data-elementor-type="wp-page"]');const lb=last.getBoundingClientRect().bottom;return {gapToInnerFooterTop:Math.round(inner.getBoundingClientRect().top-lb), outerTop:Math.round(f.getBoundingClientRect().top-lb)}});
console.log(w,JSON.stringify(r)); await p.evaluate(()=>window.scrollTo(0,document.body.scrollHeight)); await p.screenshot({path:'wp/shots/ft-'+w+'.png'}); await p.close();}
await b.close();})();
