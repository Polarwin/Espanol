// End-to-end offline pack test with a temporary HTTP origin and real MP3/PDF.
const { chromium } = require('/home/justin/tmp-reinforcement-browser/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const http = require('node:http');
const { execFileSync } = require('node:child_process');
(async () => {
 const root = fs.mkdtempSync(path.join(os.tmpdir(), 'vamos-offline-test-'));
 execFileSync('./bin/python', ['-c', `
import json,sys,shutil
from pathlib import Path
from tools.subtitle_reading import render
from tools.reading_folder_cache import publish_folder_worker
root=Path(sys.argv[1])/'SpanishReading'
publish_folder_worker(root)
root=root/'A2'/'2026-10-13'
root.mkdir(parents=True)
source=next(p.parent for p in Path('/srv/files/static/SpanishReading').glob('*/*/*/ejercicio.json') if (p.parent/'ejercicio.pdf').is_file() and (p.parent/'lectura.mp3').is_file())
for name in ('one','two'):
 d=root/name;d.mkdir()
 pack=json.loads((source/'ejercicio.json').read_text())
 pack.update(title=name,pdf_file='ejercicio.pdf',audio_file='lectura.mp3')
 pack['vocabulary']=[{'term':'pan','spanish':'Un alimento hecho con harina.','english':'Food made from flour and water.'},{'term':'casa','spanish':'Un lugar donde vive una persona.','english':'A place where a person lives.'}]
 for file,text in render(pack).items(): (d/file).write_text(text)
 for file in ('lectura.mp3','ejercicio.pdf'): shutil.copyfile(source/file,d/file)
`, root]);
 const server = http.createServer((req,res) => {
  const file = path.join(root, decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if (!file.startsWith(root+path.sep) || !fs.existsSync(file)) { res.writeHead(404);res.end();return; }
  if(fs.statSync(file).isDirectory()){res.setHeader('Content-Type','text/html');res.end(fs.readdirSync(file).map(name=>`<a href="${name}${fs.statSync(path.join(file,name)).isDirectory()?'/':''}">${name}</a>`).join('<br>'));return;}
  res.setHeader('Content-Type', file.endsWith('.js')?'application/javascript':file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.pdf')?'application/pdf':'audio/mpeg');
  res.end(fs.readFileSync(file));
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const host=`http://127.0.0.1:${server.address().port}`;
 const origin=host+'/SpanishReading/A2/2026-10-13';
 const browser=await chromium.launch({headless:true,executablePath:'/home/justin/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell',args:['--autoplay-policy=no-user-gesture-required']});
 try {
  const context=await browser.newContext();const page=await context.newPage();const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  for(const name of ['one','two']) {
   await page.goto(`${origin}/${name}/ejercicio.html`);
   await page.locator('#offline-status').filter({hasText:'Listo sin conexión'}).waitFor({timeout:120000});
   await page.waitForFunction(()=>!!navigator.serviceWorker.controller);
  }
  await page.locator('#offline-check').click();
  await page.waitForFunction(()=>!document.querySelector('#offline-check').disabled);
  assert.equal(await page.locator('#offline-files').isVisible(),true);
  assert.equal(await page.locator('#offline-files li').count(),12);
  assert.equal(await page.locator('#offline-files li[data-cached="false"]').count(),0);
  assert.ok(await page.locator('#offline-files').innerText().then(text=>text.includes('ejercicio.pdf')&&text.includes('lectura.mp3')));
  await page.evaluate(async()=>{for(const name of await caches.keys())if(name.includes('/two/:'))await (await caches.open(name)).delete(new URL('lectura.mp3',location.href).href)});
  await page.locator('#offline-check').click();
  await page.waitForFunction(()=>!document.querySelector('#offline-check').disabled);
  assert.match(await page.locator('#offline-status').innerText(),/Listo sin conexión/);
  assert.equal(await page.locator('#offline-files li[data-cached="false"]').count(),0);
  await context.setOffline(true);
  await page.locator('#offline-check').click();
  await page.waitForFunction(()=>!document.querySelector('#offline-check').disabled);
  assert.match(await page.locator('#offline-status').innerText(),/Listo sin conexión/);
  await page.goto(host+'/SpanishReading/');
  await page.getByRole('link',{name:'A2',exact:true}).click();
  await page.getByRole('link',{name:'2026-10-13',exact:true}).click();
  await page.getByRole('link',{name:'two',exact:true}).click();
  await page.getByRole('link',{name:'ejercicio.html',exact:true}).click();
  assert.match(await page.locator('#offline-status').innerText(),/Preparando|Comprobando|Listo/);
  await page.goto(`${origin}/one/tarjetas.html`);
  assert.equal(await page.locator('#card').innerText(),'pan');
  await page.locator('#card').click();assert.match(await page.locator('#card').innerText(),/flour/);
  await page.locator('#known').click();await page.reload();assert.match(await page.locator('#progress').innerText(),/1 aprendidas/);
  await page.locator('#next').click();assert.equal(await page.locator('#card').innerText(),'casa');
  const results=await page.evaluate(async()=>{
   const pdf=await fetch('ejercicio.pdf');const bytes=await pdf.arrayBuffer();
   const audio=await fetch('lectura.mp3',{headers:{Range:'bytes=4-31'}});
   return {pdf:pdf.status,pdfMagic:new TextDecoder().decode(bytes.slice(0,4)),range:audio.status,length:(await audio.arrayBuffer()).byteLength};
  });
  assert.deepEqual(results,{pdf:200,pdfMagic:'%PDF',range:206,length:28});
  await page.goto(`${origin}/one/escuchar.html`);
  await page.waitForFunction(()=>document.querySelector('audio').readyState>=1);
  await page.locator('audio').evaluate(async a=>{a.currentTime=1;await a.play()});
  await page.waitForFunction(()=>document.querySelector('audio').currentTime>1.1);
  assert.deepEqual(errors,[]);
  console.log('PASS: offline root/level/date/pack navigation; automatic whole-pack preload; offline cards, saved progress, PDF, audio playback/seeking, and independent pack caches.');
 } finally {await browser.close();await new Promise(resolve=>server.close(resolve));fs.rmSync(root,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1});
