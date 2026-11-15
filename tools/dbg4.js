const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
const hits=[];p.on('request',r=>{if(/openwidget/.test(r.url()))hits.push(r.url().slice(0,60));});
await p.goto('https://staging.cigalacycling.com/?x='+Date.now(),{waitUntil:'networkidle'});await p.waitForTimeout(2000);
console.log('start: chat btn',await p.isVisible('#cc-chat'),'banner',await p.isVisible('#cc-consent'),'ow requests',hits.length);
await p.screenshot({path:'wp/shots/chatbtn.png',clip:{x:0,y:640,width:1440,height:260}});
await p.click('#cc-chat');await p.waitForTimeout(6000);
console.log('after click: ow requests',hits.length,'btn',await p.isVisible('#cc-chat'),'iframes',await p.evaluate(()=>[...document.querySelectorAll('iframe')].map(f=>f.src.slice(0,50)+' '+f.offsetWidth+'x'+f.offsetHeight)));
await p.screenshot({path:'wp/shots/chatopen.png'});await b.close();})();
