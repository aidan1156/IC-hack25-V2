
self.addEventListener('install',function(event){
    event.waitUntil(
        caches.open('sw-cache').then(function(cache){
            return cache.addAll([//the basic caches we need 
            ]);
        })
    );
});

self.addEventListener('fetch',function(event){
    event.respondWith(
        caches.match(event.request).then((resp) => {
            return fetch(event.request)
        })
    );
});


self.addEventListener('activate', async () => {
    // This will be called only once when the service worker is activated.
    
})
