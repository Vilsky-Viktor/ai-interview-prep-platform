import { LRUMap } from '@sentry/core';
import { WINDOW } from '@sentry/react';
import { maybeParameterizeRoute, getManifest } from './parameterization.js';

const IS_ISR_SSG_ROUTE_CACHE = new LRUMap(100);
function isIsrSsgRoute(pathname) {
  const parameterizedPath = maybeParameterizeRoute(pathname);
  const pathToCheck = parameterizedPath || pathname;
  const cachedResult = IS_ISR_SSG_ROUTE_CACHE.get(pathToCheck);
  if (cachedResult !== void 0) {
    return cachedResult;
  }
  const manifest = getManifest();
  if (!manifest?.isrRoutes || !Array.isArray(manifest.isrRoutes) || manifest.isrRoutes.length === 0) {
    IS_ISR_SSG_ROUTE_CACHE.set(pathToCheck, false);
    return false;
  }
  const isIsrSsgRoute2 = manifest.isrRoutes.includes(pathToCheck);
  IS_ISR_SSG_ROUTE_CACHE.set(pathToCheck, isIsrSsgRoute2);
  return isIsrSsgRoute2;
}
function removeIsrSsgTraceMetaTags() {
  if (!WINDOW.document || !isIsrSsgRoute(WINDOW.location.pathname)) {
    return;
  }
  function removeMetaTag(metaName) {
    try {
      const meta = WINDOW.document.querySelector(`meta[name="${metaName}"]`);
      if (meta) {
        meta.remove();
      }
    } catch {
    }
  }
  removeMetaTag("sentry-trace");
  removeMetaTag("baggage");
}

export { IS_ISR_SSG_ROUTE_CACHE, isIsrSsgRoute, removeIsrSsgTraceMetaTags };
//# sourceMappingURL=isrRoutingTracing.js.map
