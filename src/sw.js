const CACHE_NAME = 'csl-atlas-v2';
const scopedUrl = (path) => new URL(path, self.registration.scope).toString();
const ASSETS_TO_CACHE = [
  scopedUrl('./'),
  scopedUrl('./index.html'),
  scopedUrl('./favicon.svg'),
  scopedUrl('./manifest.json')
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      try {
        const networkResponse = await fetch(event.request);
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          await cache.put(event.request, networkResponse.clone());
          return networkResponse;
        }
        // Network is reachable but the response is unusable (server error or
        // opaque). Prefer a cached copy when we have one rather than handing
        // back a 5xx/error page in place of content we already hold.
        if (!networkResponse || networkResponse.status >= 500) {
          const cachedResponse = await caches.match(event.request);
          if (cachedResponse) return cachedResponse;
        }
        return networkResponse;
      } catch {
        const cachedResponse = await caches.match(event.request);
        if (cachedResponse) return cachedResponse;
        if (event.request.mode === 'navigate') {
          const cachedIndex = await caches.match(scopedUrl('./index.html'));
          if (cachedIndex) return cachedIndex;
        }
        return new Response('', { status: 504, statusText: 'Offline' });
      }
    })()
  );
});
