const CACHE='unidad1-offline:'+self.registration.scope+':fa1615d8db4da09f';
const PAGE=new URL('index.html',self.registration.scope).href;
self.addEventListener('install',e=>e.waitUntil((async()=>{const cache=await caches.open(CACHE);await cache.add(new Request(PAGE,{cache:'reload'}));await self.skipWaiting()})()));
self.addEventListener('activate',e=>e.waitUntil((async()=>{for(const name of await caches.keys())if(name.startsWith('unidad1-offline:'+self.registration.scope+':')&&name!==CACHE)await caches.delete(name);await self.clients.claim()})()));
self.addEventListener('fetch',e=>{const url=new URL(e.request.url);if(e.request.method!=='GET'||url.origin!==self.location.origin)return;if(url.pathname===new URL(PAGE).pathname||url.href===self.registration.scope)e.respondWith((async()=>await(await caches.open(CACHE)).match(PAGE)||fetch(e.request))())});
