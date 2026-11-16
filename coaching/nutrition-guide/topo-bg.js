// Bakes the brand topo background (58% dim overlay) into one A4-ratio JPEG, so the PDF stays small.
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const tmp = path.resolve(__dirname, 'assets/_topo.html');
  fs.writeFileSync(tmp, `<body style="margin:0;width:1588px;height:2246px;background:linear-gradient(rgba(8,9,10,.58),rgba(8,9,10,.58)),#08090a url(topo-background.svg) center/cover no-repeat"></body>`);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1588, height: 2246 } });
  await p.goto('file://' + tmp, { waitUntil: 'networkidle' });
  await p.screenshot({ path: path.resolve(__dirname, 'assets/topo-a4.jpg'), type: 'jpeg', quality: 82 });
  await b.close(); fs.unlinkSync(tmp);
})();
