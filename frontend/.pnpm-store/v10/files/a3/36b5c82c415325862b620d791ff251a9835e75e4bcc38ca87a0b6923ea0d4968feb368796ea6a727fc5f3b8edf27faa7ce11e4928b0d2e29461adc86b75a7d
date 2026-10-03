Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const attributes = require('@sentry/conventions/attributes');
const op = require('@sentry/conventions/op');
const core = require('@sentry/core');
const browser = require('@sentry/core/browser');
const debugBuild = require('../debug-build.js');
const htmlTreeAsString = require('../htmlTreeAsString.js');
const performanceObserver = require('../instrumentation/performanceObserver.js');
const inp = require('../web-vitals/inp.js');
const isBotUserAgent = require('../isBotUserAgent.js');
const types = require('../types.js');
const utils = require('./utils.js');
const componentName = require('../component-name.js');

const INTEGRATION_NAME = "Interactions";
const _interactionsIntegration = ((options = {}) => {
  return {
    name: INTEGRATION_NAME,
    setup(client) {
      if (isBotUserAgent.isBotUserAgent()) {
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
        const { name, attributes: attributes$1 } = core.spanToJSON(span);
        latestRoute.name = name;
        latestRoute.source = attributes$1[attributes.SENTRY_SOURCE] || attributes$1[attributes.SENTRY_SEGMENT_NAME_SOURCE];
        latestRoute.routeId = attributes$1[attributes.ROUTER_NAVIGATION_ROUTE_ID];
        latestRoute.urlTemplate = attributes$1[attributes.URL_TEMPLATE];
        latestRoute.httpRoute = attributes$1[attributes.HTTP_ROUTE];
        latestRoute.urlPath = attributes$1[attributes.URL_PATH];
        latestRoute.urlFull = attributes$1[attributes.URL_FULL];
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
const interactionsIntegration = core.defineIntegration(_interactionsIntegration);
function isRouteSpan(span) {
  if (core.getRootSpan(span) !== span) {
    return false;
  }
  const op = core.spanToJSON(span).attributes[attributes.SENTRY_OP];
  return op === "pageload" || op === "navigation";
}
function registerInteractionListener(client, latestRoute, getInflightRouteSpan, idleSpanOptions) {
  if (!types.WINDOW.document) {
    return;
  }
  let inflightInteractionSpan;
  addEventListener(
    "click",
    () => {
      if (getInflightRouteSpan()) {
        debugBuild.DEBUG_BUILD && core.debug.warn(
          `[Tracing] Did not create ${op.UI_ACTION_CLICK} span because a pageload or navigation span is in progress.`
        );
        return;
      }
      if (inflightInteractionSpan) {
        inflightInteractionSpan.setAttribute(attributes.SENTRY_IDLE_SPAN_FINISH_REASON, "interactionInterrupted");
        inflightInteractionSpan.end();
        inflightInteractionSpan = void 0;
      }
      if (!latestRoute.name) {
        debugBuild.DEBUG_BUILD && core.debug.warn(`[Tracing] Did not create ${op.UI_ACTION_CLICK} span because the latest route name is missing.`);
        return;
      }
      const hasSpanStreaming = core.hasSpanStreamingEnabled(client);
      const routeName = latestRoute.routeId || latestRoute.urlTemplate || latestRoute.httpRoute;
      const streamedName = routeName || core.UI_ACTION_CLICK_SPAN_NAME_FALLBACK;
      const streamedNameSource = !routeName || latestRoute.routeId ? "custom" : "route";
      inflightInteractionSpan = browser.startIdleSpan(
        {
          name: hasSpanStreaming ? streamedName : latestRoute.name,
          attributes: {
            [attributes.SENTRY_OP]: op.UI_ACTION_CLICK,
            [attributes.SENTRY_SEGMENT_NAME_SOURCE]: hasSpanStreaming ? streamedNameSource : latestRoute.source || "url",
            [attributes.SENTRY_ORIGIN]: "auto.browser.interactions",
            ...hasSpanStreaming && { [attributes.SENTRY_SEGMENT_NAME]: streamedName },
            ...latestRoute.routeId && { [attributes.ROUTER_NAVIGATION_ROUTE_ID]: latestRoute.routeId },
            ...latestRoute.urlTemplate && { [attributes.URL_TEMPLATE]: latestRoute.urlTemplate },
            ...latestRoute.httpRoute && { [attributes.HTTP_ROUTE]: latestRoute.httpRoute },
            ...latestRoute.urlPath && { [attributes.URL_PATH]: latestRoute.urlPath },
            ...latestRoute.urlFull && { [attributes.URL_FULL]: core.filterCollectedUrl(latestRoute.urlFull) }
          }
        },
        idleSpanOptions
      );
    },
    { capture: true }
  );
}
function trackInteractionsAsSpans(client) {
  performanceObserver.addPerformanceInstrumentationHandler("event", ({ entries }) => {
    const parent = core.getActiveSpan();
    if (!parent) {
      return;
    }
    for (const entry of entries) {
      if (entry.name === "click") {
        const startTime = utils.msToSec(core.browserPerformanceTimeOrigin() + entry.startTime);
        const duration = utils.msToSec(entry.duration);
        const selector = htmlTreeAsString.htmlTreeAsString(entry.target);
        const componentName$1 = componentName.getComponentName(entry.target);
        const hasSpanStreaming = core.hasSpanStreamingEnabled(client);
        const spanOptions = {
          name: hasSpanStreaming ? componentName$1 || core.UI_INTERACTION_CLICK_SPAN_NAME_FALLBACK : selector,
          startTime,
          attributes: {
            [attributes.SENTRY_OP]: op.UI_INTERACTION_CLICK,
            [attributes.SENTRY_ORIGIN]: "auto.browser.interactions",
            ...selector && selector !== inp.UNKNOWN_ELEMENT_NAME && { [attributes.BROWSER_WEB_VITAL_INP_TARGET]: selector }
          }
        };
        if (componentName$1) {
          spanOptions.attributes[attributes.UI_COMPONENT_NAME] = componentName$1;
        }
        utils.startAndEndSpan(parent, startTime, startTime + duration, spanOptions);
      }
    }
  });
}

exports.interactionsIntegration = interactionsIntegration;
//# sourceMappingURL=interactions.js.map
