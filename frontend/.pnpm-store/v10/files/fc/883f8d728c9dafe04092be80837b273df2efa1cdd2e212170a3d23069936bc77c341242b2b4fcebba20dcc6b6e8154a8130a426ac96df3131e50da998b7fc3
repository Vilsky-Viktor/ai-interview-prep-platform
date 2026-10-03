Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const react = require('@sentry/react');
const parameterization = require('./parameterization.js');

const IS_ISR_SSG_ROUTE_CACHE = new core.LRUMap(100);
function isIsrSsgRoute(pathname) {
  const parameterizedPath = parameterization.maybeParameterizeRoute(pathname);
  const pathToCheck = parameterizedPath || pathname;
  const cachedResult = IS_ISR_SSG_ROUTE_CACHE.get(pathToCheck);
  if (cachedResult !== void 0) {
    return cachedResult;
  }
  const manifest = parameterization.getManifest();
  if (!manifest?.isrRoutes || !Array.isArray(manifest.isrRoutes) || manifest.isrRoutes.length === 0) {
    IS_ISR_SSG_ROUTE_CACHE.set(pathToCheck, false);
    return false;
  }
  const isIsrSsgRoute2 = manifest.isrRoutes.includes(pathToCheck);
  IS_ISR_SSG_ROUTE_CACHE.set(pathToCheck, isIsrSsgRoute2);
  return isIsrSsgRoute2;
}
function removeIsrSsgTraceMetaTags() {
  if (!react.WINDOW.document || !isIsrSsgRoute(react.WINDOW.location.pathname)) {
    return;
  }
  function removeMetaTag(metaName) {
    try {
      const meta = react.WINDOW.document.querySelector(`meta[name="${metaName}"]`);
      if (meta) {
        meta.remove();
      }
    } catch {
    }
  }
  removeMetaTag("sentry-trace");
  removeMetaTag("baggage");
}

exports.IS_ISR_SSG_ROUTE_CACHE = IS_ISR_SSG_ROUTE_CACHE;
exports.isIsrSsgRoute = isIsrSsgRoute;
exports.removeIsrSsgTraceMetaTags = removeIsrSsgTraceMetaTags;
//# sourceMappingURL=isrRoutingTracing.js.map
