/**
 * AgriSmart AI — Service Worker for offline support and caching.
 * Implements a cache-first strategy for static assets and network-first
 * for API calls, enabling basic offline functionality for field use.
 */

const CACHE_NAME = "agrismart-v1";
const STATIC_CACHE = "agrismart-static-v1";
const API_CACHE = "agrismart-api-v1";

// Static assets to pre-cache on install
const PRECACHE_ASSETS = [
  "/",
  "/static/index.html",
  "/static/style.css",
  "/static/app.js",
  "/static/logo.svg",
  "/static/manifest.json",
];

// ---------------------------------------------------------------------------
// Install: pre-cache critical static assets
// ---------------------------------------------------------------------------
self.addEventListener("install", (event) => {
  console.log("[SW] Installing AgriSmart service worker...");
  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => {
        console.log("[SW] Pre-caching static assets");
        return cache.addAll(PRECACHE_ASSETS);
      })
      .catch((err) => {
        console.warn("[SW] Pre-cache failed (non-critical):", err);
      })
  );
  self.skipWaiting();
});

// ---------------------------------------------------------------------------
// Activate: clean up old caches
// ---------------------------------------------------------------------------
self.addEventListener("activate", (event) => {
  console.log("[SW] Activating service worker...");
  const currentCaches = [STATIC_CACHE, API_CACHE];
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => !currentCaches.includes(name))
          .map((name) => {
            console.log("[SW] Removing old cache:", name);
            return caches.delete(name);
          })
      )
    )
  );
  self.clients.claim();
});

// ---------------------------------------------------------------------------
// Fetch: cache-first for static, network-first for API
// ---------------------------------------------------------------------------
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET requests
  if (event.request.method !== "GET") return;

  // API calls: network-first with cache fallback
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Cache successful API responses for offline use
          if (response.ok && url.pathname.startsWith("/api/weather/")) {
            const responseClone = response.clone();
            caches.open(API_CACHE).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Offline: try cache fallback for weather data
          return caches.match(event.request).then((cached) => {
            if (cached) {
              console.log("[SW] Serving cached API response:", url.pathname);
              return cached;
            }
            return new Response(
              JSON.stringify({
                error: "offline",
                message: "No network connection. Cached data unavailable.",
              }),
              {
                status: 503,
                headers: { "Content-Type": "application/json" },
              }
            );
          });
        })
    );
    return;
  }

  // Static assets: cache-first strategy
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) {
        // Return cached version, update in background
        fetch(event.request)
          .then((response) => {
            if (response.ok) {
              caches.open(STATIC_CACHE).then((cache) => {
                cache.put(event.request, response);
              });
            }
          })
          .catch(() => {});
        return cached;
      }

      // Not in cache: fetch from network
      return fetch(event.request).then((response) => {
        if (response.ok) {
          const responseClone = response.clone();
          caches.open(STATIC_CACHE).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      });
    })
  );
});

// ---------------------------------------------------------------------------
// Background sync placeholder for offline prediction queue
// ---------------------------------------------------------------------------
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-predictions") {
    console.log("[SW] Background sync: uploading queued predictions");
    // Future: dequeue offline predictions and POST to /api/predict
  }
});

console.log("[SW] AgriSmart service worker loaded.");
