const CACHE_NAME = 'dreamtime-bush-trail-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  // Add more static assets as needed
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
}); 