/* Run: NODE_PATH=/tmp/vozes-senado-qa/node_modules node tests/browser.cjs */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/opt/google/chrome/chrome',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1080}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.DASHBOARD_URL||'http://127.0.0.1:8000';
 try{
  await page.goto(base);await page.locator('#dashboard').waitFor({state:'visible'});
  assert.equal(await page.locator('#kpi-count').innerText(),'4.045');
  assert.equal(await page.locator('#kpi-authors').innerText(),'106');
  assert.equal(await page.locator('.month-bar').count(),48);
  await page.screenshot({path:'/tmp/vozes-senado-desktop.png',fullPage:true});
  await page.selectOption('#kind','');assert.equal(await page.locator('#kpi-count').innerText(),'12.414');
  await page.click('#reset');await page.selectOption('#party','PT');await page.selectOption('#uf','RS');await page.selectOption('#author','825');
  assert.equal(await page.locator('#kpi-count').innerText(),'442');assert.equal(await page.locator('#kpi-authors').innerText(),'1');
  assert.ok((await page.locator('#records').innerText()).includes('Paulo Paim'));
  await page.click('#reset');await page.fill('#query','educação');await page.waitForTimeout(250);const accentCount=await page.locator('#kpi-count').innerText();
  await page.fill('#query','EDUCACAO');await page.waitForTimeout(250);assert.equal(await page.locator('#kpi-count').innerText(),accentCount);
  await page.fill('#query','zzzz-no-match-2026');await page.waitForTimeout(250);assert.equal(await page.locator('#kpi-count').innerText(),'0');assert.ok(await page.locator('#export').isDisabled());assert.ok((await page.locator('#records').innerText()).includes('Não há registros'));
  await page.click('#reset');await page.locator('[data-mode="share"]').click();assert.ok((await page.locator('#timeline svg').getAttribute('aria-label')).includes('por cento'));
  await page.locator('.month-bar').first().focus();await page.keyboard.press('Enter');assert.equal(await page.locator('#from').inputValue(),'2019-02');assert.equal(await page.locator('#to').inputValue(),'2019-02');assert.equal(await page.locator('.month-bar').count(),1);
  await page.click('#reset');await page.locator('#authors-chart button').first().click();assert.equal(await page.locator('#author').inputValue(),'825');
  await page.click('#reset');await page.locator('#themes-chart button').first().click();assert.notEqual(await page.locator('#theme').inputValue(),'');
  await page.click('#reset');await page.click('#next');assert.equal(await page.locator('#page-info').innerText(),'Página 2 de 506');await page.click('#prev');
  await page.selectOption('#sort','oldest');const dates=await page.locator('.record-date').allTextContents();assert.equal(dates[0],'02/02/2019');
  await page.fill('#from','2022-01');await page.fill('#to','2020-01');await page.locator('#to').dispatchEvent('change');assert.ok(await page.locator('#filter-error').isVisible());assert.equal(await page.locator('#kpi-count').innerText(),'0');
  await page.click('#reset');
  const downloadPromise=page.waitForEvent('download');await page.click('#export');const download=await downloadPromise;
  const file=await download.path();const csv=await fs.readFile(file,'utf8');assert.equal(csv.split('\r\n').length,4046);assert.ok(csv.includes('partido_na_data'));
  const href=await page.locator('#records a').first().getAttribute('href');assert.match(href,/^https:\/\/www25\.senado\.leg\.br\/web\/atividade\/pronunciamentos\/-\/p\/texto\/\d+$/);
  const localLinks=await page.locator('a[href$=".md"],a[href$=".json"]').evaluateAll(els=>els.map(e=>e.href));
  for(const url of localLinks){const response=await page.request.get(url);assert.equal(response.status(),200,url);}
  await page.setViewportSize({width:390,height:844});await page.goto(base);await page.locator('#dashboard').waitFor({state:'visible'});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'mobile page should not overflow');
  await page.screenshot({path:'/tmp/vozes-senado-mobile.png',fullPage:true});
  await page.selectOption('#uf','AC');assert.notEqual(await page.locator('#kpi-count').innerText(),'4.045');
  const failure=await browser.newPage();await failure.route('**/data/dashboard.json',route=>route.fulfill({status:404,body:'missing'}));await failure.goto(base);
  await failure.locator('#load-status[role="alert"]').waitFor();assert.ok((await failure.locator('#load-status').innerText()).includes('README'));await failure.close();
  assert.deepEqual(errors,[]);
  console.log('PASS: load, totals, 48 months, combined filters, accent search, empty, percent, keyboard drilldown, authors, themes, pagination, sorting, invalid dates, CSV 4045 rows, source links, local docs, mobile, error state; no JS errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
