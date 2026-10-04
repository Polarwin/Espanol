const CACHE='palabra-v1';
const FILES=['./','index.html','EspanolFlashcards-offline.html','manifest.webmanifest','icon.svg','icon-192.png','icon-512.png','CONJUGATION-LICENSE.txt'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim().then(async()=>{for(const key of await caches.keys())if(key.startsWith('palabra-')&&key!==CACHE)await caches.delete(key);for(const client of await self.clients.matchAll())client.postMessage('OFFLINE_READY');})));
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(event.request.method!=='GET'||url.origin!==location.origin||!url.pathname.startsWith(new URL(self.registration.scope).pathname))return;
 event.respondWith(caches.match(event.request).then(hit=>hit||fetch(event.request)));
});
