"""Publish a worker at the reading root so cached directory URLs work offline."""
WORKER = '''const CACHE='vamos-reading-folders:'+self.registration.scope;
self.addEventListener('install',event=>event.waitUntil(self.skipWaiting()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(event.request.method!=='GET'||!url.href.startsWith(self.registration.scope))return;
 if(url.pathname.endsWith('/'))event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  try{const response=await fetch(event.request);if(response.ok)await cache.put(event.request,response.clone());return response}
  catch(error){const saved=await cache.match(event.request);if(saved)return saved;throw error}
 })());
 else event.respondWith((async()=>await caches.match(event.request)||fetch(event.request))());
});
'''


def publish_folder_worker(root):
    root.mkdir(parents=True, exist_ok=True)
    temporary = root / '.reading-folders-sw.js.tmp'
    temporary.write_text(WORKER, encoding='utf-8')
    temporary.replace(root / 'reading-folders-sw.js')
