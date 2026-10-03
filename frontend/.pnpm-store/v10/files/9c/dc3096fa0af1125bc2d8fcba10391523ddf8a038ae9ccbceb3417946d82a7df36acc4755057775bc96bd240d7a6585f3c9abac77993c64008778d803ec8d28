import { TRACING_DEFAULTS, consoleSandbox, hasSpanStreamingEnabled, PAGELOAD_SPAN_NAME_FALLBACK, parseStringToURLObject, NAVIGATION_SPAN_NAME_FALLBACK, debug, registerSpanErrorInstrumentation, GLOBAL_OBJ, getCurrentScope, getDynamicSamplingContextFromSpan, spanIsSampled, getClient, hasSpansEnabled, generateSpanId, generateTraceId, propagationContextFromHeaders, spanToJSON, browserPerformanceTimeOrigin, dateTimestampInSeconds, timestampInSeconds, addNonEnumerableProperty, isURLObjectRelative, filterCollectedUrl } from '@sentry/core';
import { _INTERNAL_ensureBrowserSpanStreaming, startInactiveSpan, startIdleSpan } from '@sentry/core/browser';
import { isBotUserAgent, getLocationHref, addHistoryInstrumentationHandler, startTrackingLongAnimationFrames, startTrackingLongTasks, addPerformanceEntries } from '@sentry/browser-utils';
import { SENTRY_IDLE_SPAN_FINISH_REASON, URL_FULL, URL_PATH, SENTRY_OP, SENTRY_SEGMENT_NAME_SOURCE, SENTRY_ORIGIN, BROWSER_NAVIGATION_TYPE } from '@sentry/conventions/attributes';
import { DEBUG_BUILD } from '../debug-build.js';
import { WINDOW, getHttpRequestData } from '../helpers.js';
import { WEB_VITALS_INTEGRATION_NAME, webVitalsIntegration } from '../integrations/webVitals.js';
import { registerBackgroundTabDetection } from './backgroundtab.js';
import { linkTraces } from './linkedTraces.js';
import { defaultRequestInstrumentationOptions, instrumentOutgoingRequests } from './request.js';
import { NAVIGATION_REDIRECT, NAVIGATION, PAGELOAD } from '@sentry/conventions/op';

const BROWSER_TRACING_INTEGRATION_ID = "BrowserTracing";
const DEFAULT_BROWSER_TRACING_OPTIONS = {
  ...TRACING_DEFAULTS,
  instrumentNavigation: true,
  instrumentBfcacheRestore: true,
  instrumentPageLoad: true,
  markBackgroundSpan: true,
  enableLongTask: true,
  enableLongAnimationFrame: true,
  // oxlint-disable-next-line typescript/no-deprecated -- still honoured until it is removed
  enableInp: true,
  ignoreResourceSpans: [],
  detectRedirects: true,
  linkPreviousTrace: "in-memory",
  consistentTraceSampling: false,
  enableReportPageLoaded: false,
  ...defaultRequestInstrumentationOptions
};
const browserTracingIntegration = ((options = {}) => {
  if ("enableElementTiming" in options) {
    consoleSandbox(() => {
      console.warn(
        "[Sentry] `enableElementTiming` is deprecated and no longer has any effect. Use the standalone `elementTimingIntegration` instead."
      );
    });
  }
  const optionalWindowDocument = WINDOW.document;
  const {
    // oxlint-disable-next-line typescript/no-deprecated -- still honoured until it is removed
    enableInp,
    enableLongTask,
    enableLongAnimationFrame,
    webVitals,
    beforeStartSpan,
    idleTimeout,
    finalTimeout,
    childSpanTimeout,
    markBackgroundSpan,
    traceFetch,
    traceXHR,
    shouldCreateSpanForRequest,
    enableHTTPTimings,
    ignoreResourceSpans,
    instrumentPageLoad,
    instrumentNavigation,
    instrumentBfcacheRestore,
    detectRedirects,
    linkPreviousTrace,
    consistentTraceSampling,
    enableReportPageLoaded,
    onRequestSpanStart,
    onRequestSpanEnd
  } = {
    ...DEFAULT_BROWSER_TRACING_OPTIONS,
    ...options
  };
  const _isBot = isBotUserAgent();
  let lastInteractionTimestamp;
  let _pageloadSpan;
  function _createRouteSpan(client, startSpanOptions, makeActive = true, url) {
    const isPageloadSpan = startSpanOptions.op === "pageload";
    const initialSpanName = startSpanOptions.name;
    const finalStartSpanOptions = beforeStartSpan ? beforeStartSpan(startSpanOptions) : startSpanOptions;
    const urlObject = parseStringToURLObject(url || getLocationHref());
    const attributes = {
      ...urlObject?.pathname && { [URL_PATH]: urlObject.pathname },
      ...urlObject && !isURLObjectRelative(urlObject) && { [URL_FULL]: filterCollectedUrl(urlObject.href) },
      ...finalStartSpanOptions.attributes
    };
    if (initialSpanName !== finalStartSpanOptions.name) {
      attributes[SENTRY_SEGMENT_NAME_SOURCE] = "custom";
    }
    finalStartSpanOptions.attributes = attributes;
    if (!makeActive) {
      const now = dateTimestampInSeconds();
      startInactiveSpan({
        ...finalStartSpanOptions,
        startTime: now
      }).end(now);
      return;
    }
    const idleSpan = startIdleSpan(finalStartSpanOptions, {
      idleTimeout,
      finalTimeout,
      childSpanTimeout,
      // should wait for finish signal if it's a pageload transaction
      disableAutoFinish: isPageloadSpan,
      trimIdleSpanEndTimestamp: !enableReportPageLoaded
    });
    if (isPageloadSpan && enableReportPageLoaded) {
      _pageloadSpan = idleSpan;
    }
    setActiveIdleSpan(client, idleSpan);
    function emitFinish() {
      if (optionalWindowDocument && ["interactive", "complete"].includes(optionalWindowDocument.readyState)) {
        client.emit("idleSpanEnableAutoFinish", idleSpan);
        optionalWindowDocument.removeEventListener("readystatechange", emitFinish);
      }
    }
    if (isPageloadSpan && !enableReportPageLoaded && optionalWindowDocument) {
      optionalWindowDocument.addEventListener("readystatechange", emitFinish);
      emitFinish();
    }
  }
  return {
    name: BROWSER_TRACING_INTEGRATION_ID,
    setup(client) {
      if (_isBot) {
        DEBUG_BUILD && debug.log("[Tracing] Skipping browserTracingIntegration setup for bot user agent.");
        return;
      }
      registerSpanErrorInstrumentation();
      if (enableLongAnimationFrame && GLOBAL_OBJ.PerformanceObserver && PerformanceObserver.supportedEntryTypes?.includes("long-animation-frame")) {
        startTrackingLongAnimationFrames();
      } else if (enableLongTask) {
        startTrackingLongTasks();
      }
      if (detectRedirects && optionalWindowDocument) {
        const interactionHandler = () => {
          lastInteractionTimestamp = timestampInSeconds();
        };
        addEventListener("click", interactionHandler, { capture: true });
        addEventListener("keydown", interactionHandler, { capture: true, passive: true });
      }
      function maybeEndActiveSpan() {
        const activeSpan = getActiveIdleSpan(client);
        if (activeSpan && !spanToJSON(activeSpan).end_timestamp) {
          DEBUG_BUILD && debug.log(
            `[Tracing] Finishing current active span with op: ${spanToJSON(activeSpan).attributes[SENTRY_OP]}`
          );
          activeSpan.setAttribute(SENTRY_IDLE_SPAN_FINISH_REASON, "cancelled");
          activeSpan.end();
        }
      }
      client.on("beforeIdleSpanEnd", (span) => {
        if (getActiveIdleSpan(client) !== span) {
          return;
        }
        addPerformanceEntries(span, {
          ignoreResourceSpans,
          spanStreamingEnabled: hasSpanStreamingEnabled(client)
        });
        setActiveIdleSpan(client, void 0);
        const scope = getCurrentScope();
        const oldPropagationContext = scope.getPropagationContext();
        scope.setPropagationContext({
          ...oldPropagationContext,
          traceId: span.spanContext().traceId,
          sampled: spanIsSampled(span),
          dsc: getDynamicSamplingContextFromSpan(span)
        });
        if (_pageloadSpan === span) {
          _pageloadSpan = void 0;
        }
      });
      client.on("startNavigationSpan", (startSpanOptions, navigationOptions) => {
        if (getClient() !== client) {
          return;
        }
        if (navigationOptions?.isRedirect) {
          DEBUG_BUILD && debug.warn("[Tracing] Detected redirect, navigation span will not be the root span, but a child span.");
          _createRouteSpan(
            client,
            {
              op: NAVIGATION_REDIRECT,
              ...startSpanOptions
            },
            false,
            navigationOptions.url
          );
          return;
        }
        lastInteractionTimestamp = void 0;
        maybeEndActiveSpan();
        const scope = getCurrentScope();
        scope.setPropagationContext({
          traceId: generateTraceId(),
          sampleRand: Math.random(),
          propagationSpanId: hasSpansEnabled() ? void 0 : generateSpanId()
        });
        scope.setSDKProcessingMetadata({
          normalizedRequest: void 0
        });
        _createRouteSpan(
          client,
          {
            op: NAVIGATION,
            ...startSpanOptions,
            // Navigation starts a new trace and is NOT parented under any active interaction (e.g. ui.action.click)
            parentSpan: null
          },
          true,
          navigationOptions?.url
        );
      });
      client.on("startPageLoadSpan", (startSpanOptions, traceOptions = {}) => {
        if (getClient() !== client) {
          return;
        }
        maybeEndActiveSpan();
        const sentryTrace = traceOptions.sentryTrace || getMetaContent("sentry-trace") || getServerTiming("sentry-trace");
        const baggage = traceOptions.baggage || getMetaContent("baggage") || getServerTiming("baggage");
        const propagationContext = propagationContextFromHeaders(sentryTrace, baggage);
        const scope = getCurrentScope();
        scope.setPropagationContext(propagationContext);
        if (!hasSpansEnabled()) {
          scope.getPropagationContext().propagationSpanId = generateSpanId();
        }
        scope.setSDKProcessingMetadata({
          normalizedRequest: getHttpRequestData()
        });
        _createRouteSpan(client, {
          op: PAGELOAD,
          ...startSpanOptions
        });
      });
      client.on("endPageloadSpan", () => {
        if (enableReportPageLoaded && _pageloadSpan) {
          _pageloadSpan.setAttribute(SENTRY_IDLE_SPAN_FINISH_REASON, "reportPageLoaded");
          _pageloadSpan.end();
        }
      });
      WINDOW.addEventListener?.("pagehide", () => {
        const activeSpan = getActiveIdleSpan(client);
        if (activeSpan && !spanToJSON(activeSpan).end_timestamp) {
          activeSpan.setAttribute(SENTRY_IDLE_SPAN_FINISH_REASON, "documentHidden");
          activeSpan.end();
        }
        void client.flush();
      });
    },
    afterAllSetup(client) {
      if (_isBot) {
        return;
      }
      _INTERNAL_ensureBrowserSpanStreaming(client);
      if (client.addIntegration && !client.getIntegrationByName?.(WEB_VITALS_INTEGRATION_NAME)) {
        const ignore = webVitals?.ignore ?? [];
        client.addIntegration(
          webVitalsIntegration({
            ...webVitals,
            ignore: enableInp || ignore.includes("inp") ? ignore : [...ignore, "inp"]
          })
        );
      }
      let startingUrl = getLocationHref();
      if (linkPreviousTrace !== "off") {
        linkTraces(client, { linkPreviousTrace, consistentTraceSampling });
      }
      if (WINDOW.location) {
        if (instrumentPageLoad) {
          startBrowserTracingPageLoadSpan(client, {
            // With span streaming, span names have to be low cardinality, and there is no route
            // information available here.
            name: hasSpanStreamingEnabled(client) ? PAGELOAD_SPAN_NAME_FALLBACK : WINDOW.location.pathname,
            attributes: {
              [SENTRY_SEGMENT_NAME_SOURCE]: "url",
              [SENTRY_ORIGIN]: "auto.pageload.browser"
            }
          });
        }
        if (instrumentNavigation) {
          addHistoryInstrumentationHandler(({ to, from }) => {
            if (from === void 0 && startingUrl !== void 0 && startingUrl.indexOf(to) !== -1) {
              startingUrl = void 0;
              return;
            }
            startingUrl = void 0;
            const parsed = parseStringToURLObject(to);
            const activeSpan = getActiveIdleSpan(client);
            const navigationIsRedirect = activeSpan && detectRedirects && isRedirect(activeSpan, lastInteractionTimestamp);
            startBrowserTracingNavigationSpan(
              client,
              {
                // With span streaming, span names have to be low cardinality, and there is no route
                // information available here.
                name: hasSpanStreamingEnabled(client) ? NAVIGATION_SPAN_NAME_FALLBACK : parsed?.pathname || WINDOW.location.pathname,
                attributes: {
                  [SENTRY_SEGMENT_NAME_SOURCE]: "url",
                  [SENTRY_ORIGIN]: "auto.navigation.browser"
                }
              },
              { url: to, isRedirect: navigationIsRedirect }
            );
          });
        }
        if (instrumentBfcacheRestore) {
          WINDOW.addEventListener?.("pageshow", (event) => {
            if (!event.persisted) {
              return;
            }
            startingUrl = void 0;
            startBrowserTracingNavigationSpan(
              client,
              {
                // Deliberately no `startTime`: the span starts now, at the restore. The
                // `PerformanceNavigationTiming` entry still describes the original document load and
                // would date the span to before the page was frozen.
                //
                // TODO(routing): resolve the parameterized route via the route provider (#23551) and set
                // the source from it. No router event fires on a restore, so in a framework app this is
                // the only navigation span still named from a raw pathname.
                name: hasSpanStreamingEnabled(client) ? NAVIGATION_SPAN_NAME_FALLBACK : WINDOW.location?.pathname || "/",
                attributes: {
                  [SENTRY_SEGMENT_NAME_SOURCE]: "url",
                  [SENTRY_ORIGIN]: "auto.navigation.browser.bfcache",
                  // A bfcache restore is near-instant, so these spans would otherwise drag
                  // navigation duration percentiles down with no way to tell them apart.
                  [BROWSER_NAVIGATION_TYPE]: "back-forward-cache"
                }
              },
              { url: WINDOW.location?.href }
            );
          });
        }
      }
      if (markBackgroundSpan) {
        registerBackgroundTabDetection();
      }
      instrumentOutgoingRequests(client, {
        traceFetch,
        traceXHR,
        tracePropagationTargets: client.getOptions().tracePropagationTargets,
        shouldCreateSpanForRequest,
        enableHTTPTimings,
        onRequestSpanStart,
        onRequestSpanEnd
      });
    }
  };
});
function startBrowserTracingPageLoadSpan(client, spanOptions, traceOptions) {
  const isFallbackSpanName = spanOptions.name === PAGELOAD_SPAN_NAME_FALLBACK;
  getCurrentScope().setTransactionName(isFallbackSpanName ? WINDOW.location?.pathname : spanOptions.name);
  const timeOrigin = browserPerformanceTimeOrigin();
  const pageloadSpanOptions = {
    ...spanOptions,
    // startTime needs to be in seconds, not ms
    startTime: spanOptions.startTime ?? (timeOrigin ? timeOrigin / 1e3 : void 0)
  };
  client.emit("startPageLoadSpan", pageloadSpanOptions, traceOptions);
  const pageloadSpan = getActiveIdleSpan(client);
  if (pageloadSpan) {
    client.emit("afterStartPageLoadSpan", pageloadSpan);
  }
  return pageloadSpan;
}
function startBrowserTracingNavigationSpan(client, spanOptions, options) {
  const { url, isRedirect: isRedirect2 } = options || {};
  client.emit("beforeStartNavigationSpan", spanOptions, { isRedirect: isRedirect2, url });
  client.emit("startNavigationSpan", spanOptions, { isRedirect: isRedirect2, url });
  const scope = getCurrentScope();
  const isFallbackSpanName = spanOptions.name === NAVIGATION_SPAN_NAME_FALLBACK;
  scope.setTransactionName(
    isFallbackSpanName ? url && parseStringToURLObject(url)?.pathname || WINDOW.location?.pathname : spanOptions.name
  );
  if (url && !isRedirect2) {
    scope.setSDKProcessingMetadata({
      normalizedRequest: {
        ...getHttpRequestData(),
        url
      }
    });
  }
  return getActiveIdleSpan(client);
}
function getMetaContent(metaName) {
  const optionalWindowDocument = WINDOW.document;
  const metaTag = optionalWindowDocument?.querySelector(`meta[name=${metaName}]`);
  return metaTag?.getAttribute("content") || void 0;
}
function getServerTiming(name) {
  const navigation = WINDOW.performance?.getEntriesByType?.("navigation")[0];
  const entry = navigation?.serverTiming?.find((entry2) => entry2.name === name);
  return entry?.description;
}
const ACTIVE_IDLE_SPAN_PROPERTY = "_sentry_idleSpan";
function getActiveIdleSpan(client) {
  return client[ACTIVE_IDLE_SPAN_PROPERTY];
}
function setActiveIdleSpan(client, span) {
  addNonEnumerableProperty(client, ACTIVE_IDLE_SPAN_PROPERTY, span);
}
const REDIRECT_THRESHOLD = 1.5;
function isRedirect(activeSpan, lastInteractionTimestamp) {
  const spanData = spanToJSON(activeSpan);
  const now = dateTimestampInSeconds();
  const startTimestamp = spanData.start_timestamp;
  if (now - startTimestamp > REDIRECT_THRESHOLD) {
    return false;
  }
  if (lastInteractionTimestamp && now - lastInteractionTimestamp <= REDIRECT_THRESHOLD) {
    return false;
  }
  return true;
}

export { BROWSER_TRACING_INTEGRATION_ID, browserTracingIntegration, getMetaContent, getServerTiming, startBrowserTracingNavigationSpan, startBrowserTracingPageLoadSpan };
//# sourceMappingURL=browserTracingIntegration.js.map
