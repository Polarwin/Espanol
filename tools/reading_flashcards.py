"""Self-contained vocabulary cards and per-pack offline caching."""
from hashlib import sha256
import html
import json


def flashcards_page(pack):
    cards = [{k: word[k] for k in ('term', 'spanish', 'english')} for word in pack['vocabulary']]
    encoded = json.dumps(cards, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    key = sha256(encoded.encode()).hexdigest()[:20]
    page = '''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tarjetas de vocabulario</title><style>
*{box-sizing:border-box}body{font:18px/1.6 system-ui,sans-serif;background:#f4f1e8;color:#183d37;max-width:800px;margin:30px auto;padding:0 20px}h1{font-size:1.7rem;line-height:1.2}button,a{touch-action:manipulation}button{font:inherit;cursor:pointer;border:1px solid #185d50;border-radius:12px;background:white;color:#183d37;padding:10px 16px}button:focus-visible,a:focus-visible{outline:3px solid #ca593b;outline-offset:3px}button:disabled{opacity:.5;cursor:default}#card{display:block;width:100%;min-height:270px;text-align:center;padding:26px;white-space:pre-line;font-size:1.4rem;box-shadow:0 4px 15px #183d3715}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}.note{font-size:.85rem;color:#556a61}a{color:#185d50}#progress{font-weight:bold}#card[data-back="true"]{font-size:1.1rem;background:#e5eee7}@media print{button,nav,.actions{display:none}}
</style><body><h1>Tarjetas de vocabulario</h1><p>''' + html.escape(pack['title']) + ''' · ''' + html.escape(pack['level']) + '''</p>
<p id="progress" aria-live="polite"></p><button id="card" type="button" aria-label="Mostrar explicación"></button>
<p class="note">Pulsa la tarjeta para girarla. Teclado: ← anterior, → siguiente; espacio o Intro para girar la tarjeta enfocada.</p>
<div class="actions"><button id="previous">← Anterior</button><button id="flip">Girar</button><button id="next">Siguiente →</button></div>
<div class="actions"><button id="known">Ya la sé</button><button id="shuffle">Mezclar</button><button id="reset">Reiniciar progreso</button></div>
<p id="saved" class="note"></p><button id="download">Descargar tarjetas HTML</button>
<p class="note">Todas las palabras y explicaciones están incluidas en este archivo. El HTML descargado funciona sin conexión.</p>
<nav><a href="ejercicio.html">Lectura</a> · <a href="escuchar.html">Escuchar</a> · <a href="traduccion.html">English translation</a></nav>
<script id="cards" type="application/json">''' + encoded + '''</script><script>
const cards=JSON.parse(document.getElementById('cards').textContent), storageKey='vamos.cards.''' + key + '''';
let order=cards.map((_,i)=>i), position=0, back=false, learned=new Set();
try{const saved=JSON.parse(localStorage.getItem(storageKey)||'[]');if(Array.isArray(saved)) learned=new Set(saved.filter(i=>Number.isInteger(i)&&i>=0&&i<cards.length));}catch{}
const get=id=>document.getElementById(id);
function render(){
 const i=order[position], c=cards[i];
 get('progress').textContent=cards.length?`${position+1} / ${cards.length} · ${learned.size} aprendidas`:'No hay vocabulario en este paquete.';
 get('card').textContent=c?(back?`${c.spanish}\n\nEnglish: ${c.english}`:c.term):'Sin tarjetas';
 get('card').dataset.back=String(back);get('card').setAttribute('aria-label',back?'Mostrar palabra':'Mostrar explicación');
 get('known').textContent=learned.has(i)?'Repasar otra vez':'Ya la sé';
 for(const id of ['card','previous','flip','next','known','shuffle'])get(id).disabled=!cards.length;
}
function flip(){back=!back;render()}
function move(step){if(!cards.length)return;position=(position+step+cards.length)%cards.length;back=false;render()}
function save(){try{localStorage.setItem(storageKey,JSON.stringify([...learned]));get('saved').textContent='Progreso guardado en este navegador.'}catch{get('saved').textContent='Progreso disponible solo durante esta sesión.'}}
get('card').onclick=flip;get('flip').onclick=flip;get('previous').onclick=()=>move(-1);get('next').onclick=()=>move(1);
get('known').onclick=()=>{const i=order[position];if(i===undefined)return;const wasLearned=learned.has(i);wasLearned?learned.delete(i):learned.add(i);save();if(!wasLearned)move(1);else render()};
get('shuffle').onclick=()=>{for(let i=order.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[order[i],order[j]]=[order[j],order[i]]}position=0;back=false;render()};
get('reset').onclick=()=>{learned.clear();save();render()};
document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'){e.preventDefault();move(-1)}if(e.key==='ArrowRight'){e.preventDefault();move(1)}});
get('download').onclick=()=>{const url=URL.createObjectURL(new Blob(['<!doctype html>'+document.documentElement.outerHTML],{type:'text/html;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='tarjetas.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
render();
</script></body></html>'''
    if pack.get('audio_file') != 'lectura.mp3':
        page = page.replace(' · <a href="escuchar.html">Escuchar</a>', '')
    return page


def add_offline(pages, pack):
    """Cache only this pack; updates replace its cache after a full download."""
    files = list(pages)
    for field, allowed in [('audio_file', 'lectura.mp3'), ('pdf_file', 'ejercicio.pdf')]:
        if pack.get(field) == allowed:
            files.append(allowed)
    version = sha256(('offline-ui-v3' + json.dumps(pack, sort_keys=True, ensure_ascii=False) + ''.join(pages.values())).encode()).hexdigest()[:20]
    files_json = json.dumps(files)
    worker = '''const FILES=__FILES__,VERSION='__VERSION__';
const PREFIX='vamos-pack:'+self.registration.scope+':',CACHE=PREFIX+VERSION;
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const cache=await caches.open(CACHE);
 try{await cache.addAll(FILES.map(file=>new Request(new URL(file,self.registration.scope),{cache:'reload'})))}catch(error){await caches.delete(CACHE);throw error}
 await self.skipWaiting();
})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 for(const name of await caches.keys())if(name.startsWith(PREFIX)&&name!==CACHE)await caches.delete(name);
 await self.clients.claim();
})()));
self.addEventListener('message',event=>{if(event.data==='STATUS'&&event.ports[0])event.ports[0].postMessage({version:VERSION})});
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(event.request.method==='GET'&&url.href===self.registration.scope){event.respondWith((async()=>await caches.match(url.href)||fetch(event.request))());return}
 if(event.request.method!=='GET'||!FILES.some(file=>new URL(file,self.registration.scope).href===url.href))return;
 event.respondWith((async()=>{
 const cached=await (await caches.open(CACHE)).match(url.href);
 if(!cached)return fetch(event.request);
 const range=event.request.headers.get('range');
 if(!range)return cached;
 const buffer=await cached.arrayBuffer(),size=buffer.byteLength,m=/^bytes=(\\d*)-(\\d*)$/.exec(range);
 if(!m||(!m[1]&&!m[2]))return new Response(null,{status:416,headers:{'Content-Range':`bytes */${size}`}});
 let start=m[1]?Number(m[1]):Math.max(0,size-Number(m[2]));
 let end=m[1]?(m[2]?Math.min(Number(m[2]),size-1):size-1):size-1;
 if(start>=size||start>end)return new Response(null,{status:416,headers:{'Content-Range':`bytes */${size}`}});
 const headers=new Headers(cached.headers);headers.set('Content-Range',`bytes ${start}-${end}/${size}`);headers.set('Content-Length',String(end-start+1));headers.set('Accept-Ranges','bytes');
 return new Response(buffer.slice(start,end+1),{status:206,headers});
 })());
});'''.replace('__FILES__', files_json).replace('__VERSION__', version)
    navigation = '<nav aria-label="Material del paquete"><a href="tarjetas.html">Tarjetas de vocabulario</a>'
    if 'ejercicio.pdf' in files:
        navigation += ' · <a href="ejercicio.pdf" download>Descargar PDF</a>'
    if 'lectura.mp3' in files:
        navigation += ' · <a href="lectura.mp3" download>Descargar audio</a>'
    navigation += '</nav><section id="offline-panel" aria-label="Disponibilidad sin conexión"><button id="offline-check" type="button" aria-controls="offline-files" aria-expanded="false">Guardar y comprobar archivos sin conexión</button><p id="offline-status" role="status" style="font:14px system-ui">Preparando este paquete sin conexión…</p><ul id="offline-files" hidden></ul></section>'
    navigation += '<style>#offline-check{font:inherit;padding:10px 16px;border:1px solid #185d50;border-radius:8px;background:#185d50;color:white;cursor:pointer}#offline-check:disabled{opacity:.6}#offline-files{font:14px/1.8 system-ui;overflow-wrap:anywhere}@media print{#offline-panel{display:none}}</style>'
    script = r'''<script>(()=>{
const status=document.getElementById('offline-status'),button=document.getElementById('offline-check'),list=document.getElementById('offline-files');
const files=__FILES__,name='vamos-pack:'+new URL('./',location.href).href+':__VERSION__';
const match=location.pathname.match(/^(.*\/SpanishReading\/)(A[12]|B[12])\/(\d{4}-\d{2}-\d{2})\/[^/]+\//);
const root=match?new URL(match[1],location.origin):null;
const folders=root?[root.href,new URL(match[2]+'/',root).href,new URL(match[2]+'/'+match[3]+'/',root).href,new URL('./',location.href).href]:[];
const folderCache=root?'vamos-reading-folders:'+root.href:null;
if(root){const nav=document.createElement('nav');nav.setAttribute('aria-label','Carpetas');
 folders.forEach((url,i)=>{if(i)nav.append(' / ');const a=document.createElement('a');a.href=url;a.textContent=['SpanishReading',match[2],match[3],'Este paquete'][i];nav.append(a)});
 document.getElementById('offline-panel').before(nav)}
let running=false;
async function prepareFolders(){
 if(!root)return;
 const registration=await navigator.serviceWorker.register(new URL('reading-folders-sw.js',root),{scope:root.href,updateViaCache:'none'});
 for(let i=0;!registration.active&&i<120;i++)await new Promise(resolve=>setTimeout(resolve,500));
 if(!registration.active)throw new Error('No se ha activado la navegación sin conexión.');
 const cache=await caches.open(folderCache);
 for(const url of folders){try{const response=await fetch(url,{cache:'reload'});if(!response.ok)throw new Error('Carpeta no disponible');await cache.put(url,response)}catch(error){if(!await cache.match(url))throw error}}
} 
async function inspect(){
 const cache=(await caches.keys()).includes(name)?await caches.open(name):null;
 const saved=await Promise.all(files.map(async file=>!!(cache&&await cache.match(new URL(file,location.href).href))));
 const directoryCache=folderCache&&(await caches.keys()).includes(folderCache)?await caches.open(folderCache):null;
 const folderSaved=await Promise.all(folders.map(async url=>!!(directoryCache&&await directoryCache.match(url))));
 const entries=[...files,...folders],states=[...saved,...folderSaved];
 list.replaceChildren(...entries.map((file,i)=>{
  const row=document.createElement('li'),link=document.createElement('a');
  link.href=file;link.textContent=i<files.length?file:new URL(file).pathname;row.dataset.cached=String(states[i]);
  row.append(link,document.createTextNode(states[i]?' — En caché ✓':' — Pendiente de guardar'));
  return row;
 }));
 return states;
}
async function prepare(manual=false){
 if(manual){list.hidden=false;button.setAttribute('aria-expanded','true')}
 if(running)return;
 running=true;button.disabled=true;
 try{
  if(!('serviceWorker' in navigator)||!isSecureContext||location.protocol==='file:')throw new Error('La precarga requiere HTTPS de confianza.');
  status.textContent='Comprobando y guardando los archivos de este paquete…';
  await inspect();
  await navigator.serviceWorker.register('./offline-sw.js',{scope:'./',updateViaCache:'none'});
  await prepareFolders();
  for(let i=0;i<240;i++){
   let saved=await inspect();
   // A manual check repairs evicted entries even if the worker is already installed.
   if(manual&&navigator.serviceWorker.controller&&!saved.every(Boolean)){
    const cache=await caches.open(name);
    await cache.addAll(files.filter((file,index)=>!saved[index]).map(file=>new Request(new URL(file,location.href),{cache:'reload'})));
    saved=await inspect();
   }
   if(saved.every(Boolean)&&navigator.serviceWorker.controller){
    status.textContent=`Listo sin conexión: ${files.length+folders.length}/${files.length+folders.length} archivos y carpetas en caché (páginas, tarjetas`+(files.includes('ejercicio.pdf')?', PDF':'')+(files.includes('lectura.mp3')?' y audio':'')+'). Guarda esta dirección. El navegador puede borrar la caché si falta espacio.';return;
   }
   await new Promise(resolve=>setTimeout(resolve,500));
  }
  throw new Error('No se han guardado todos los archivos.');
 }catch(error){
  status.textContent='Precarga incompleta. Mantén la conexión y pulsa el botón para reintentar. '+error.message;
  try{await inspect()}catch{list.replaceChildren();const row=document.createElement('li');row.textContent='No se puede acceder a la caché de este navegador.';list.append(row)}
 }finally{running=false;button.disabled=false}
}
button.onclick=()=>prepare(true);prepare();
})();</script>'''.replace('__FILES__', files_json).replace('__VERSION__', version)
    for name in list(pages):
        pages[name] = pages[name].replace('<body>', '<body>'+navigation, 1).replace('</body>', script+'</body>')
    pages['offline-sw.js'] = worker
    return pages
