Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const browser = require('@sentry/browser');
const core = require('@sentry/core');
const attributes = require('@sentry/conventions/attributes');
const op = require('@sentry/conventions/op');

function reactRouterV3BrowserTracingIntegration(options) {
  const integration = browser.browserTracingIntegration({
    ...options,
    instrumentPageLoad: false,
    instrumentNavigation: false
  });
  const { history, routes, match, instrumentPageLoad = true, instrumentNavigation = true } = options;
  return {
    ...integration,
    afterAllSetup(client) {
      integration.afterAllSetup(client);
      if (instrumentPageLoad && browser.WINDOW.location) {
        normalizeTransactionName(
          routes,
          browser.WINDOW.location,
          match,
          (localName, source = "url") => {
            browser.startBrowserTracingPageLoadSpan(client, {
              // With span streaming, span names have to be low cardinality, so we can't fall back to the URL.
              name: source === "route" || !core.hasSpanStreamingEnabled(client) ? localName : core.PAGELOAD_SPAN_NAME_FALLBACK,
              attributes: {
                [attributes.SENTRY_OP]: op.PAGELOAD,
                [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.pageload.react.reactrouter_v3",
                [attributes.SENTRY_SEGMENT_NAME_SOURCE]: source,
                ...source === "route" && { [attributes.URL_TEMPLATE]: localName }
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
                browser.startBrowserTracingNavigationSpan(client, {
                  // With span streaming, span names have to be low cardinality, so we can't fall back to the URL.
                  name: source === "route" || !core.hasSpanStreamingEnabled(client) ? localName : core.NAVIGATION_SPAN_NAME_FALLBACK,
                  attributes: {
                    [attributes.SENTRY_OP]: op.NAVIGATION,
                    [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.navigation.react.reactrouter_v3",
                    [attributes.SENTRY_SEGMENT_NAME_SOURCE]: source,
                    ...source === "route" && { [attributes.URL_TEMPLATE]: localName }
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

exports.reactRouterV3BrowserTracingIntegration = reactRouterV3BrowserTracingIntegration;
//# sourceMappingURL=reactrouterv3.js.map
