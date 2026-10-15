/* QA: NODE_PATH=/tmp/vozes-senado-qa/node_modules DASHBOARD_URL=http://127.0.0.1:8001 node tests/browser.cjs */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/opt/google/chrome/chrome',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1080}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.DASHBOARD_URL||'http://127.0.0.1:8000';
 const ready=async()=>{await page.waitForFunction(()=>document.getElementById('dashboard')?.getAttribute('aria-busy')==='false');await page.locator('#exploracao').evaluate(el=>el.open=true);};
 const select=async(id,v)=>{await page.selectOption('#'+id,v);await ready();};
 const click=async(selector)=>{await page.click(selector);await ready();};
 const count=async n=>{await page.waitForFunction(n=>document.getElementById('kpi-count').textContent===n,n);await ready();};
 const query=async value=>{await page.fill('#query',value);await page.waitForTimeout(350);await ready();};
 try{
  await page.goto(base);await ready();
  assert.equal(await page.locator('#kpi-count').innerText(),'4.045');assert.equal(await page.locator('#kpi-authors').innerText(),'106');assert.equal(await page.locator('.month-bar').count(),48);
  const resources=await page.evaluate(()=>performance.getEntriesByType('resource').map(r=>({name:r.name,bytes:r.encodedBodySize})));const initialBytes=resources.reduce((n,r)=>n+r.bytes,0);
  assert.ok(!resources.some(r=>r.name.endsWith('/dashboard.json')));assert.ok(resources.filter(r=>r.name.includes('/details/')).length<=2);assert.ok(initialBytes<1000000,`initial resource payload ${initialBytes}`);
  console.log('Initial bytes:',initialBytes,'resources:',resources.length);
  await fs.writeFile('/tmp/vozes-v2-performance.json',JSON.stringify({viewport:'1440x1080',initialBytes,resources},null,2));
  await page.screenshot({path:'/tmp/vozes-v2-desktop.png',fullPage:true});
  assert.ok((await page.locator('#compare-summary').innerText()).includes('1.788'));assert.ok((await page.locator('#compare-warning').innerText()).includes('Mesma duração'));
  await page.fill('#aFrom','2021-02');await page.fill('#aTo','2021-12');await ready();await click('#compare-next-year');assert.equal(await page.locator('#bFrom').inputValue(),'2022-02');assert.equal(await page.locator('#bTo').inputValue(),'2022-12');
  await page.fill('#bTo','2022-06');await ready();assert.ok((await page.locator('#compare-warning').innerText()).includes('Duração diferente'));
  await click('#reset');await select('kind','');await count('12.414');await click('#reset');await select('party','PT');await select('uf','RS');await select('author','825');await count('442');
  assert.ok((await page.locator('#records').innerText()).includes('Paulo Paim'));
  await click('#reset');await query('educação');const accentCount=await page.locator('#kpi-count').innerText();await query('EDUCACAO');assert.equal(await page.locator('#kpi-count').innerText(),accentCount);
  await query('zzzz-no-match-2026');await count('0');assert.ok(await page.locator('#export').isDisabled());assert.ok((await page.locator('#records').innerText()).includes('Não há registros'));assert.ok((await page.locator('#compare-summary').innerText()).includes('indefinida'));
  await click('#reset');await click('[data-mode="share"]');assert.ok((await page.locator('#timeline svg').getAttribute('aria-label')).includes('por cento'));
  await page.locator('.month-bar').first().focus();await page.keyboard.press('Enter');await ready();assert.equal(await page.locator('#from').inputValue(),'2019-02');assert.equal(await page.locator('.month-bar').count(),1);
  await click('#reset');await click('#authors-chart button:first-of-type');assert.equal(await page.locator('#author').inputValue(),'825');
  await click('#reset');await click('#themes-chart button:first-of-type');assert.notEqual(await page.locator('#theme').inputValue(),'');
  await click('#reset');await click('#next');assert.equal(await page.locator('#page-info').innerText(),'Página 2 de 506');await click('#prev');
  await select('sort','oldest');assert.equal(await page.locator('.record-date').first().innerText(),'02/02/2019');
  await page.fill('#from','2022-01');await page.fill('#to','2020-01');await ready();assert.ok(await page.locator('#filter-error').isVisible());await count('0');await click('#reset');
  // URL restores every analytical selection, and Back/Forward restores history.
  await select('party','PT');await select('trend','Educação');await select('quality','kind');await select('voice2','825');await click('[data-mode="share"]');const savedURL=page.url();
  await page.reload();await ready();assert.equal(await page.locator('#party').inputValue(),'PT');assert.equal(await page.locator('#trend').inputValue(),'Educação');assert.equal(await page.locator('#quality').inputValue(),'kind');assert.equal(await page.locator('#voice2').inputValue(),'825');assert.equal(await page.locator('[data-mode="share"]').getAttribute('aria-pressed'),'true');assert.equal(page.url(),savedURL);
  await select('uf','RS');await page.goBack();await ready();assert.equal(await page.locator('#uf').inputValue(),'');await page.goForward();await ready();assert.equal(await page.locator('#uf').inputValue(),'RS');
  await click('#share');await page.waitForFunction(()=>/copiado|Copie/.test(document.getElementById('share-status').textContent));
  await click('#reset');assert.ok((await page.locator('#historical-context').innerText()).includes('20/03/2020'));assert.ok((await page.locator('#concentration-title').innerText()).includes('metade'));
  await page.locator('#concentracao details summary').click();
  assert.equal(await page.locator('#cumulative-table tbody tr:last-child td:last-child').innerText(),'100%');
  await select('trend','Educação');await page.locator('#trend-chart circle[role="button"]').first().focus();await page.keyboard.press('Enter');await ready();assert.equal(await page.locator('#theme').inputValue(),'Educação');assert.equal(await page.locator('#from').inputValue(),await page.locator('#to').inputValue());
  await click('#reset');await click('#quality-all-types');await count('12.414');assert.equal(await page.locator('#quality').inputValue(),'kind');assert.ok((await page.locator('#quality-chart').innerText()).includes('623'));
  await click('#reset');await page.locator('#records details').first().locator('summary').click();assert.ok((await page.locator('#records details').first().innerText()).includes('Indexação original'));
  // Real downloads; ZIP verified independently by Python after this test.
  let pending=page.waitForEvent('download');await page.click('#export');let dl=await pending;let csv=await fs.readFile(await dl.path(),'utf8');assert.equal(csv.split('\r\n').length,4046);
  pending=page.waitForEvent('download');await page.click('#export-package');dl=await pending;await dl.saveAs('/tmp/vozes-v2-analysis.zip');
  // Human audit stays empty until explicitly annotated; imports validated.
  await page.click('#open-review');await page.locator('.review-card').waitFor();assert.ok((await page.locator('#assisted-summary').innerText()).includes('5 divergências'));assert.ok((await page.locator('#review-metrics').innerText()).includes('60 pendentes'));
  await page.fill('#reviewer','QA — anotação sintética de teste');await page.locator('[name="review-label"][value="yes"]').check();await page.fill('#review-note','Teste automatizado; não representa revisão humana científica.');assert.ok((await page.locator('#review-metrics').innerText()).includes('1 pares decididos'));
  pending=page.waitForEvent('download');await page.click('#review-export');dl=await pending;const review=JSON.parse(await fs.readFile(await dl.path(),'utf8'));assert.equal(Object.keys(review.annotations).length,1);
  await page.reload();await ready();await page.click('#open-review');await page.locator('.review-card').waitFor();assert.equal(await page.locator('#reviewer').inputValue(),'QA — anotação sintética de teste');assert.ok(await page.locator('[name="review-label"][value="yes"]').isChecked());
  await page.setInputFiles('#review-import',{name:'invalid.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({...review,datasetRevision:'wrong'}))});await page.waitForFunction(()=>document.getElementById('review-status').textContent.includes('recusada'));assert.ok((await page.locator('#review-metrics').innerText()).includes('1 pares decididos'));
  await page.setInputFiles('#review-import',{name:'valid.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(review))});await page.waitForFunction(()=>document.getElementById('review-status').textContent.includes('importada'));
  // Mobile: native vertical monthly bars, ample hit areas and no page overflow.
  await page.setViewportSize({width:390,height:844});await page.goto(base);await ready();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  assert.ok(await page.locator('#timeline-mobile').isVisible());assert.equal(await page.locator('#timeline').isVisible(),false);
  await page.locator('.month-mobile-row').first().click();await ready();assert.equal(await page.locator('#from').inputValue(),'2019-02');await click('#reset');
  await page.screenshot({path:'/tmp/vozes-v2-mobile.png',fullPage:true});
  // Resource failures never silently export incomplete data; cache allows retry.
  const failure=await browser.newPage();await failure.route('**/data/catalog.json',route=>route.fulfill({status:404,body:'missing'}));await failure.goto(base);await failure.locator('#load-status[role="alert"]').waitFor();assert.ok((await failure.locator('#load-status').innerText()).includes('README'));await failure.close();
  const broken=await browser.newPage();await broken.route('**/data/details/*.json',route=>route.fulfill({status:503,body:'temporarily unavailable'}));await broken.goto(base);await broken.locator('#operation-error').waitFor({state:'visible'});assert.equal(await broken.locator('#kpi-count').innerText(),'4.045');await broken.unroute('**/data/details/*.json');await broken.locator('#operation-error button').click();await broken.locator('#records article').first().waitFor();await broken.close();
  const links=await page.locator('a[href$=".md"],a[href$=".json"]').evaluateAll(els=>els.map(e=>e.href));for(const url of links){const res=await page.request.get(url);assert.equal(res.status(),200,url);}
  assert.deepEqual(errors,[]);console.log('PASS v2: original flows + A/B, URL reload/history, copy link, thematic evolution, cumulative distribution, author pair, quality, evidence, CSV/ZIP, audit persistence/import/export, mobile monthly bars, catalog and shard recovery; zero JS errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
