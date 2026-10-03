Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const browser = require('@sentry/browser');
const core = require('@sentry/core');
const attributes = require('@sentry/conventions/attributes');
const op = require('@sentry/conventions/op');

function tanstackRouterBrowserTracingIntegration(router, options = {}) {
  const castRouterInstance = router;
  const browserTracingIntegrationInstance = browser.browserTracingIntegration({
    ...options,
    instrumentNavigation: false,
    instrumentPageLoad: false
  });
  const { instrumentPageLoad = true, instrumentNavigation = true } = options;
  return {
    ...browserTracingIntegrationInstance,
    afterAllSetup(client) {
      browserTracingIntegrationInstance.afterAllSetup(client);
      const resolveRouteMatch = (pathname, search) => {
        const matchedRoutes = castRouterInstance.matchRoutes(pathname, search, {
          preload: false,
          throwOnError: false
        });
        const lastMatch = matchedRoutes[matchedRoutes.length - 1];
        return lastMatch?.routeId !== "__root__" ? lastMatch : void 0;
      };
      const applyRouteMatch = (span, match, toLocation, fallbackName) => {
        span.updateName(match ? match.routeId : fallbackName);
        span.setAttribute(attributes.SENTRY_SEGMENT_NAME_SOURCE, match ? "route" : "url");
        span.setAttributes({
          ...match && { [attributes.URL_TEMPLATE]: match.routeId },
          ...locationToSpanUrlAttributes(castRouterInstance, toLocation),
          ...routeMatchToParamSpanAttributes(match)
        });
      };
      const initialWindowLocation = browser.WINDOW.location;
      if (instrumentPageLoad && initialWindowLocation) {
        const initialRouterLocation = castRouterInstance.state?.location;
        const routeMatch = initialRouterLocation ? resolveRouteMatch(initialRouterLocation.pathname, initialRouterLocation.search) : resolveRouteMatch(
          initialWindowLocation.pathname,
          castRouterInstance.options.parseSearch(initialWindowLocation.search)
        );
        const pageloadSpan = browser.startBrowserTracingPageLoadSpan(client, {
          // With span streaming, span names have to be low cardinality, so we can't fall back to the URL.
          name: routeMatch ? routeMatch.routeId : core.hasSpanStreamingEnabled(client) ? core.PAGELOAD_SPAN_NAME_FALLBACK : initialWindowLocation.pathname,
          attributes: {
            [attributes.SENTRY_OP]: op.PAGELOAD,
            [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.pageload.react.tanstack_router",
            [attributes.SENTRY_SEGMENT_NAME_SOURCE]: routeMatch ? "route" : "url",
            ...routeMatch && { [attributes.URL_TEMPLATE]: routeMatch.routeId },
            ...routeMatchToParamSpanAttributes(routeMatch)
          }
        });
        const unsubscribePageloadResolved = castRouterInstance.subscribe("onResolved", (onResolvedArgs) => {
          unsubscribePageloadResolved();
          if (!pageloadSpan) {
            return;
          }
          const { toLocation } = onResolvedArgs;
          const resolvedMatch = resolveRouteMatch(toLocation.pathname, toLocation.search);
          applyRouteMatch(
            pageloadSpan,
            resolvedMatch,
            toLocation,
            core.hasSpanStreamingEnabled(client) ? core.PAGELOAD_SPAN_NAME_FALLBACK : toLocation.pathname
          );
        });
      }
      if (instrumentNavigation) {
        let inFlightNavigationSpan;
        castRouterInstance.subscribe("onBeforeLoad", (onBeforeLoadArgs) => {
          const { toLocation, fromLocation } = onBeforeLoadArgs;
          if (!fromLocation || toLocation.state === fromLocation.state) {
            return;
          }
          const routeMatch = resolveRouteMatch(toLocation.pathname, toLocation.search);
          const fallbackName = core.hasSpanStreamingEnabled(client) ? core.NAVIGATION_SPAN_NAME_FALLBACK : browser.WINDOW.location?.pathname || toLocation.pathname;
          if (inFlightNavigationSpan) {
            applyRouteMatch(inFlightNavigationSpan, routeMatch, toLocation, fallbackName);
            return;
          }
          inFlightNavigationSpan = browser.startBrowserTracingNavigationSpan(
            client,
            {
              name: routeMatch ? routeMatch.routeId : fallbackName,
              attributes: {
                [attributes.SENTRY_OP]: op.NAVIGATION,
                [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.navigation.react.tanstack_router",
                [attributes.SENTRY_SEGMENT_NAME_SOURCE]: routeMatch ? "route" : "url",
                ...routeMatch && { [attributes.URL_TEMPLATE]: routeMatch.routeId },
                ...routeMatchToParamSpanAttributes(routeMatch)
              }
            },
            { url: locationToAbsoluteUrl(castRouterInstance, toLocation) }
          );
        });
        castRouterInstance.subscribe("onResolved", (onResolvedArgs) => {
          const span = inFlightNavigationSpan;
          inFlightNavigationSpan = void 0;
          if (!span) {
            return;
          }
          const { toLocation } = onResolvedArgs;
          const resolvedMatch = resolveRouteMatch(toLocation.pathname, toLocation.search);
          if (resolvedMatch) {
            applyRouteMatch(
              span,
              resolvedMatch,
              toLocation,
              core.hasSpanStreamingEnabled(client) ? core.NAVIGATION_SPAN_NAME_FALLBACK : browser.WINDOW.location?.pathname || toLocation.pathname
            );
          }
        });
      }
    }
  };
}
function locationToAbsoluteUrl(router, location) {
  const search = router.options.stringifySearch?.(location.search) ?? "";
  const pathWithSearch = `${location.pathname}${search && search !== "?" ? search : ""}`;
  return browser.getAbsoluteUrl(pathWithSearch);
}
function locationToSpanUrlAttributes(router, location) {
  const absoluteUrl = locationToAbsoluteUrl(router, location);
  return {
    [attributes.URL_PATH]: location.pathname,
    [attributes.URL_FULL]: core.filterCollectedUrl(absoluteUrl)
  };
}
function routeMatchToParamSpanAttributes(match) {
  if (!match) {
    return {};
  }
  const paramAttributes = {};
  Object.entries(match.params).forEach(([key, value]) => {
    paramAttributes[`${attributes.URL_PATH_PARAMETER_KEY_BASE}.${key}`] = value;
    paramAttributes[`${attributes.PARAMS_KEY_BASE}.${key}`] = value;
  });
  return paramAttributes;
}

exports.tanstackRouterBrowserTracingIntegration = tanstackRouterBrowserTracingIntegration;
//# sourceMappingURL=tanstackrouter.js.map
