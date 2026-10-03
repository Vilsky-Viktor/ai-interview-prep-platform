import { SENTRY_OP, SENTRY_SOURCE, SENTRY_SEGMENT_NAME_SOURCE, ROUTER_NAVIGATION_ROUTE_ID, URL_TEMPLATE, HTTP_ROUTE, URL_PATH, URL_FULL, SENTRY_SEGMENT_NAME, SENTRY_ORIGIN, SENTRY_IDLE_SPAN_FINISH_REASON, BROWSER_WEB_VITAL_INP_TARGET, UI_COMPONENT_NAME } from '@sentry/conventions/attributes';
import { UI_ACTION_CLICK, UI_INTERACTION_CLICK } from '@sentry/conventions/op';
import { defineIntegration, getRootSpan, spanToJSON, debug, hasSpanStreamingEnabled, UI_ACTION_CLICK_SPAN_NAME_FALLBACK, filterCollectedUrl, getActiveSpan, browserPerformanceTimeOrigin, UI_INTERACTION_CLICK_SPAN_NAME_FALLBACK } from '@sentry/core';
import { startIdleSpan } from '@sentry/core/browser';
import { DEBUG_BUILD } from '../debug-build.js';
import { htmlTreeAsString } from '../htmlTreeAsString.js';
import { addPerformanceInstrumentationHandler } from '../instrumentation/performanceObserver.js';
import { UNKNOWN_ELEMENT_NAME } from '../web-vitals/inp.js';
import { isBotUserAgent } from '../isBotUserAgent.js';
import { WINDOW } from '../types.js';
import { msToSec, startAndEndSpan } from './utils.js';
import { getComponentName } from '../component-name.js';

const INTEGRATION_NAME = "Interactions";
const _interactionsIntegration = ((options = {}) => {
  return {
    name: INTEGRATION_NAME,
    setup(client) {
      if (isBotUserAgent()) {
        return;
      }
      const latestRoute = {
        name: void 0,
        source: void 0,
        routeId: void 0,
        urlTemplate: void 0,
        httpRoute: void 0,
        urlPath: void 0,
        urlFull: void 0
      };
      let inflightRouteSpan;
      function trackRoute(span) {
        const { name, attributes } = spanToJSON(span);
        latestRoute.name = name;
        latestRoute.source = attributes[SENTRY_SOURCE] || attributes[SENTRY_SEGMENT_NAME_SOURCE];
        latestRoute.routeId = attributes[ROUTER_NAVIGATION_ROUTE_ID];
        latestRoute.urlTemplate = attributes[URL_TEMPLATE];
        latestRoute.httpRoute = attributes[HTTP_ROUTE];
        latestRoute.urlPath = attributes[URL_PATH];
        latestRoute.urlFull = attributes[URL_FULL];
      }
      client.on("spanStart", (span) => {
        if (isRouteSpan(span)) {
          inflightRouteSpan = span;
          trackRoute(span);
        }
      });
      client.on("spanEnd", (span) => {
        if (span !== inflightRouteSpan) {
          return;
        }
        inflightRouteSpan = void 0;
        trackRoute(span);
      });
      registerInteractionListener(client, latestRoute, () => inflightRouteSpan, options);
      trackInteractionsAsSpans(client);
    }
  };
});
const interactionsIntegration = defineIntegration(_interactionsIntegration);
function isRouteSpan(span) {
  if (getRootSpan(span) !== span) {
    return false;
  }
  const op = spanToJSON(span).attributes[SENTRY_OP];
  return op === "pageload" || op === "navigation";
}
function registerInteractionListener(client, latestRoute, getInflightRouteSpan, idleSpanOptions) {
  if (!WINDOW.document) {
    return;
  }
  let inflightInteractionSpan;
  addEventListener(
    "click",
    () => {
      if (getInflightRouteSpan()) {
        DEBUG_BUILD && debug.warn(
          `[Tracing] Did not create ${UI_ACTION_CLICK} span because a pageload or navigation span is in progress.`
        );
        return;
      }
      if (inflightInteractionSpan) {
        inflightInteractionSpan.setAttribute(SENTRY_IDLE_SPAN_FINISH_REASON, "interactionInterrupted");
        inflightInteractionSpan.end();
        inflightInteractionSpan = void 0;
      }
      if (!latestRoute.name) {
        DEBUG_BUILD && debug.warn(`[Tracing] Did not create ${UI_ACTION_CLICK} span because the latest route name is missing.`);
        return;
      }
      const hasSpanStreaming = hasSpanStreamingEnabled(client);
      const routeName = latestRoute.routeId || latestRoute.urlTemplate || latestRoute.httpRoute;
      const streamedName = routeName || UI_ACTION_CLICK_SPAN_NAME_FALLBACK;
      const streamedNameSource = !routeName || latestRoute.routeId ? "custom" : "route";
      inflightInteractionSpan = startIdleSpan(
        {
          name: hasSpanStreaming ? streamedName : latestRoute.name,
          attributes: {
            [SENTRY_OP]: UI_ACTION_CLICK,
            [SENTRY_SEGMENT_NAME_SOURCE]: hasSpanStreaming ? streamedNameSource : latestRoute.source || "url",
            [SENTRY_ORIGIN]: "auto.browser.interactions",
            ...hasSpanStreaming && { [SENTRY_SEGMENT_NAME]: streamedName },
            ...latestRoute.routeId && { [ROUTER_NAVIGATION_ROUTE_ID]: latestRoute.routeId },
            ...latestRoute.urlTemplate && { [URL_TEMPLATE]: latestRoute.urlTemplate },
            ...latestRoute.httpRoute && { [HTTP_ROUTE]: latestRoute.httpRoute },
            ...latestRoute.urlPath && { [URL_PATH]: latestRoute.urlPath },
            ...latestRoute.urlFull && { [URL_FULL]: filterCollectedUrl(latestRoute.urlFull) }
          }
        },
        idleSpanOptions
      );
    },
    { capture: true }
  );
}
function trackInteractionsAsSpans(client) {
  addPerformanceInstrumentationHandler("event", ({ entries }) => {
    const parent = getActiveSpan();
    if (!parent) {
      return;
    }
    for (const entry of entries) {
      if (entry.name === "click") {
        const startTime = msToSec(browserPerformanceTimeOrigin() + entry.startTime);
        const duration = msToSec(entry.duration);
        const selector = htmlTreeAsString(entry.target);
        const componentName = getComponentName(entry.target);
        const hasSpanStreaming = hasSpanStreamingEnabled(client);
        const spanOptions = {
          name: hasSpanStreaming ? componentName || UI_INTERACTION_CLICK_SPAN_NAME_FALLBACK : selector,
          startTime,
          attributes: {
            [SENTRY_OP]: UI_INTERACTION_CLICK,
            [SENTRY_ORIGIN]: "auto.browser.interactions",
            ...selector && selector !== UNKNOWN_ELEMENT_NAME && { [BROWSER_WEB_VITAL_INP_TARGET]: selector }
          }
        };
        if (componentName) {
          spanOptions.attributes[UI_COMPONENT_NAME] = componentName;
        }
        startAndEndSpan(parent, startTime, startTime + duration, spanOptions);
      }
    }
  });
}

export { interactionsIntegration };
//# sourceMappingURL=interactions.js.map
