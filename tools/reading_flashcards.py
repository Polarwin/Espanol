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
get('known').onclick=()=>{const i=order[position];learned.has(i)?learned.delete(i):learned.add(i);save();render()};
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
    version = sha256((json.dumps(pack, sort_keys=True, ensure_ascii=False) + ''.join(pages.values())).encode()).hexdigest()[:20]
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
    navigation += '</nav><p id="offline-status" role="status" style="font:14px system-ui">Preparando este paquete sin conexión…</p><button id="offline-retry" type="button" hidden>Reintentar descarga sin conexión</button>'
    navigation += '<style>@media print{#offline-status,#offline-retry{display:none}}</style>'
    script = '''<script>(()=>{
const status=document.getElementById('offline-status'),retry=document.getElementById('offline-retry');
async function prepare(){
 retry.hidden=true;
 if(!('serviceWorker' in navigator)||!isSecureContext||location.protocol==='file:'){status.textContent='Para usar sin conexión, descarga el PDF, el audio y las tarjetas HTML. La precarga requiere HTTPS de confianza.';return}
 status.textContent='Descargando páginas, PDF y audio de este paquete…';
 try{
  await navigator.serviceWorker.register('./offline-sw.js',{scope:'./',updateViaCache:'none'});
  const name='vamos-pack:'+new URL('./',location.href).href+':__VERSION__';
  for(let i=0;i<240;i++){
   if((await caches.keys()).includes(name)){
    const cache=await caches.open(name),files=__FILES__;
    if((await Promise.all(files.map(file=>cache.match(new URL(file,location.href).href)))).every(Boolean)){
     status.textContent='Listo sin conexión: páginas, tarjetas'+(files.includes('ejercicio.pdf')?', PDF':'')+(files.includes('lectura.mp3')?' y audio':'')+'. Guarda esta dirección; el navegador puede borrar descargas si falta espacio.';return;
    }
   }
   await new Promise(resolve=>setTimeout(resolve,500));
  }
  throw new Error('Download incomplete');
 }catch{status.textContent='Descarga sin conexión incompleta. Mantén la conexión y reintenta, o descarga los archivos con los enlaces.';retry.hidden=false}
}
retry.onclick=prepare;prepare();
})();</script>'''.replace('__FILES__', files_json).replace('__VERSION__', version)
    for name in list(pages):
        pages[name] = pages[name].replace('<body>', '<body>'+navigation, 1).replace('</body>', script+'</body>')
    pages['offline-sw.js'] = worker
    return pages
