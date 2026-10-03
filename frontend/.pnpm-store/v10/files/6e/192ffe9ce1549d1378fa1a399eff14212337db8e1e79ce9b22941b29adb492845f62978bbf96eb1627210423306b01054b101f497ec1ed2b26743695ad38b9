import { browserTracingIntegration, WINDOW, startBrowserTracingPageLoadSpan, startBrowserTracingNavigationSpan } from '@sentry/browser';
import { PAGELOAD_SPAN_NAME_FALLBACK, SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN, hasSpanStreamingEnabled, NAVIGATION_SPAN_NAME_FALLBACK } from '@sentry/core';
import { URL_TEMPLATE, SENTRY_SEGMENT_NAME_SOURCE, SENTRY_OP } from '@sentry/conventions/attributes';
import { PAGELOAD, NAVIGATION } from '@sentry/conventions/op';

function reactRouterV3BrowserTracingIntegration(options) {
  const integration = browserTracingIntegration({
    ...options,
    instrumentPageLoad: false,
    instrumentNavigation: false
  });
  const { history, routes, match, instrumentPageLoad = true, instrumentNavigation = true } = options;
  return {
    ...integration,
    afterAllSetup(client) {
      integration.afterAllSetup(client);
      if (instrumentPageLoad && WINDOW.location) {
        normalizeTransactionName(
          routes,
          WINDOW.location,
          match,
          (localName, source = "url") => {
            startBrowserTracingPageLoadSpan(client, {
              // With span streaming, span names have to be low cardinality, so we can't fall back to the URL.
              name: source === "route" || !hasSpanStreamingEnabled(client) ? localName : PAGELOAD_SPAN_NAME_FALLBACK,
              attributes: {
                [SENTRY_OP]: PAGELOAD,
                [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.pageload.react.reactrouter_v3",
                [SENTRY_SEGMENT_NAME_SOURCE]: source,
                ...source === "route" && { [URL_TEMPLATE]: localName }
              }
            });
          }
        );
      }
      if (instrumentNavigation && history.listen) {
        history.listen((location) => {
          if (location.action === "PUSH" || location.action === "POP") {
            normalizeTransactionName(
              routes,
              location,
              match,
              (localName, source = "url") => {
                startBrowserTracingNavigationSpan(client, {
                  // With span streaming, span names have to be low cardinality, so we can't fall back to the URL.
                  name: source === "route" || !hasSpanStreamingEnabled(client) ? localName : NAVIGATION_SPAN_NAME_FALLBACK,
                  attributes: {
                    [SENTRY_OP]: NAVIGATION,
                    [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.navigation.react.reactrouter_v3",
                    [SENTRY_SEGMENT_NAME_SOURCE]: source,
                    ...source === "route" && { [URL_TEMPLATE]: localName }
                  }
                });
              }
            );
          }
        });
      }
    }
  };
}
function normalizeTransactionName(appRoutes, location, match, callback) {
  let name = location.pathname;
  match(
    {
      location,
      routes: appRoutes
    },
    (error, _redirectLocation, renderProps) => {
      if (error || !renderProps) {
        return callback(name);
      }
      const routePath = getRouteStringFromRoutes(renderProps.routes || []);
      if (routePath.length === 0 || routePath === "/*") {
        return callback(name);
      }
      name = routePath;
      return callback(name, "route");
    }
  );
}
function getRouteStringFromRoutes(routes) {
  if (!Array.isArray(routes) || routes.length === 0) {
    return "";
  }
  const routesWithPaths = routes.filter((route) => !!route.path);
  let index = -1;
  for (let x = routesWithPaths.length - 1; x >= 0; x--) {
    const route = routesWithPaths[x];
    if (route.path?.startsWith("/")) {
      index = x;
      break;
    }
  }
  return routesWithPaths.slice(index).reduce((acc, { path }) => {
    const pathSegment = acc === "/" || acc === "" ? path : `/${path}`;
    return `${acc}${pathSegment}`;
  }, "");
}

export { reactRouterV3BrowserTracingIntegration };
//# sourceMappingURL=reactrouterv3.js.map
