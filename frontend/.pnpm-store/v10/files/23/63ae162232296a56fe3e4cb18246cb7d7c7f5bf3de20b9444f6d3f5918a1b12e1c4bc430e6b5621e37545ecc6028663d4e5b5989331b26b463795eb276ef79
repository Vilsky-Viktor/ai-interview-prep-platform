import { browserTracingIntegration, WINDOW, startBrowserTracingPageLoadSpan, startBrowserTracingNavigationSpan, getAbsoluteUrl } from '@sentry/browser';
import { PAGELOAD_SPAN_NAME_FALLBACK, SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN, hasSpanStreamingEnabled, NAVIGATION_SPAN_NAME_FALLBACK, filterCollectedUrl } from '@sentry/core';
import { URL_TEMPLATE, SENTRY_SEGMENT_NAME_SOURCE, SENTRY_OP, URL_PATH_PARAMETER_KEY_BASE, PARAMS_KEY_BASE, URL_FULL, URL_PATH } from '@sentry/conventions/attributes';
import { PAGELOAD, NAVIGATION } from '@sentry/conventions/op';

function tanstackRouterBrowserTracingIntegration(router, options = {}) {
  const castRouterInstance = router;
  const browserTracingIntegrationInstance = browserTracingIntegration({
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
        span.setAttribute(SENTRY_SEGMENT_NAME_SOURCE, match ? "route" : "url");
        span.setAttributes({
          ...match && { [URL_TEMPLATE]: match.routeId },
          ...locationToSpanUrlAttributes(castRouterInstance, toLocation),
          ...routeMatchToParamSpanAttributes(match)
        });
      };
      const initialWindowLocation = WINDOW.location;
      if (instrumentPageLoad && initialWindowLocation) {
        const initialRouterLocation = castRouterInstance.state?.location;
        const routeMatch = initialRouterLocation ? resolveRouteMatch(initialRouterLocation.pathname, initialRouterLocation.search) : resolveRouteMatch(
          initialWindowLocation.pathname,
          castRouterInstance.options.parseSearch(initialWindowLocation.search)
        );
        const pageloadSpan = startBrowserTracingPageLoadSpan(client, {
          // With span streaming, span names have to be low cardinality, so we can't fall back to the URL.
          name: routeMatch ? routeMatch.routeId : hasSpanStreamingEnabled(client) ? PAGELOAD_SPAN_NAME_FALLBACK : initialWindowLocation.pathname,
          attributes: {
            [SENTRY_OP]: PAGELOAD,
            [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.pageload.react.tanstack_router",
            [SENTRY_SEGMENT_NAME_SOURCE]: routeMatch ? "route" : "url",
            ...routeMatch && { [URL_TEMPLATE]: routeMatch.routeId },
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
            hasSpanStreamingEnabled(client) ? PAGELOAD_SPAN_NAME_FALLBACK : toLocation.pathname
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
          const fallbackName = hasSpanStreamingEnabled(client) ? NAVIGATION_SPAN_NAME_FALLBACK : WINDOW.location?.pathname || toLocation.pathname;
          if (inFlightNavigationSpan) {
            applyRouteMatch(inFlightNavigationSpan, routeMatch, toLocation, fallbackName);
            return;
          }
          inFlightNavigationSpan = startBrowserTracingNavigationSpan(
            client,
            {
              name: routeMatch ? routeMatch.routeId : fallbackName,
              attributes: {
                [SENTRY_OP]: NAVIGATION,
                [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.navigation.react.tanstack_router",
                [SENTRY_SEGMENT_NAME_SOURCE]: routeMatch ? "route" : "url",
                ...routeMatch && { [URL_TEMPLATE]: routeMatch.routeId },
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
              hasSpanStreamingEnabled(client) ? NAVIGATION_SPAN_NAME_FALLBACK : WINDOW.location?.pathname || toLocation.pathname
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
  return getAbsoluteUrl(pathWithSearch);
}
function locationToSpanUrlAttributes(router, location) {
  const absoluteUrl = locationToAbsoluteUrl(router, location);
  return {
    [URL_PATH]: location.pathname,
    [URL_FULL]: filterCollectedUrl(absoluteUrl)
  };
}
function routeMatchToParamSpanAttributes(match) {
  if (!match) {
    return {};
  }
  const paramAttributes = {};
  Object.entries(match.params).forEach(([key, value]) => {
    paramAttributes[`${URL_PATH_PARAMETER_KEY_BASE}.${key}`] = value;
    paramAttributes[`${PARAMS_KEY_BASE}.${key}`] = value;
  });
  return paramAttributes;
}

export { tanstackRouterBrowserTracingIntegration };
//# sourceMappingURL=tanstackrouter.js.map
