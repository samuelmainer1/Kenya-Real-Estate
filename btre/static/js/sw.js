// Service Worker for caching
const CACHE_NAME = 'kenya-realestate-platform-v1';
const urlsToCache = [
  '/',
  '/static/css/bootstrap.css',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/webfonts/fa-solid-900.woff2'
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
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});