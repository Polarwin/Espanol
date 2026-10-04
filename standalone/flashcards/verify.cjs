// Run with node standalone/flashcards/verify.cjs on the build machine.
const {chromium}=require('/home/justin/tmp-reinforcement-browser/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path='/srv/files/static/EspanolFlashcards/';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/home/justin/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell'});
 const context=await browser.newContext({viewport:{width:390,height:844},acceptDownloads:true});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await context.setOffline(true);
 await page.goto('file://'+path+'EspanolFlashcards-offline.html');
 await page.getByRole('button',{name:'Empezar · 10 tarjetas',exact:true}).click();
 for(let i=0;i<10;i++){
  await page.getByRole('button',{name:/Girar tarjeta/}).click();
  await page.getByRole('button',{name:i===0?'Otra vez No la recordaba':'Lo sabía Seguimos →',exact:true}).click();
 }
 await page.getByText('Recordaste 9 de 10 tarjetas sin dificultad.',{exact:true}).waitFor();
 await page.getByRole('button',{name:'Repasar estas 1 tarjetas',exact:true}).click();
 await page.getByRole('button',{name:/Girar tarjeta/}).click();
 await page.keyboard.press('3');
 await page.getByText('Recordaste 1 de 1 tarjetas sin dificultad.',{exact:true}).waitFor();
 assert.equal(await page.locator('#learned').innerText(),'10');
 await page.reload();assert.equal(await page.locator('#learned').innerText(),'10');
 await page.getByRole('button',{name:'Explorar la biblioteca'}).click();
 await page.getByRole('searchbox').fill('conocerse');
 await page.locator('.wordrow').filter({hasText:'conocerse a uno/a mismo/a'}).first().click();
 await page.getByText('me conozco',{exact:true}).waitFor();
 await page.getByRole('combobox',{name:'Tiempo verbal'}).selectOption('Perfecto');
 await page.getByText('me he conocido',{exact:true}).waitFor();
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.screenshot({path:'/tmp/flashcards-mobile.png',fullPage:true});
 await page.getByText('Guardar mi progreso',{exact:true}).click();
 const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'Exportar progreso'}).click();const download=await downloadPromise;
 await download.saveAs('/tmp/flashcards-progress-test.json');
 const exported=JSON.parse(fs.readFileSync('/tmp/flashcards-progress-test.json'));assert.equal(Object.keys(exported.state.cards).length,10);
 await page.locator('#importFile').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{"app":"not-our-app"}')});
 await page.getByText(/No se pudo importar/).waitFor();assert.equal(await page.locator('#learned').innerText(),'10');
 const other=await browser.newContext({viewport:{width:1300,height:950}});await other.setOffline(true);const otherPage=await other.newPage();
 await otherPage.goto('file://'+path+'EspanolFlashcards-offline.html');
 await otherPage.locator('#importFile').setInputFiles('/tmp/flashcards-progress-test.json');
 await otherPage.getByText('Progreso importado: 10 tarjetas actualizadas.',{exact:true}).waitFor();
 await otherPage.getByRole('button',{name:'Empezar · 10 tarjetas',exact:true}).click();
 await otherPage.getByRole('button',{name:/Girar tarjeta/}).click();
 await otherPage.screenshot({path:'/tmp/flashcards-desktop.png',fullPage:true});
 assert.deepEqual(errors,[]);
 console.log('PASS: standalone file offline, 10-card rounds, mistakes retry, keyboard, conjugations, persistence, export/import, mobile layout');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
