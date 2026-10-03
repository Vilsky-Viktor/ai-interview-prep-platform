Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const browser = require('@sentry/core/browser');
const browserUtils = require('@sentry/browser-utils');
const attributes = require('@sentry/conventions/attributes');
const debugBuild = require('../debug-build.js');
const helpers = require('../helpers.js');
const webVitals = require('../integrations/webVitals.js');
const backgroundtab = require('./backgroundtab.js');
const linkedTraces = require('./linkedTraces.js');
const request = require('./request.js');
const op = require('@sentry/conventions/op');

const BROWSER_TRACING_INTEGRATION_ID = "BrowserTracing";
const DEFAULT_BROWSER_TRACING_OPTIONS = {
  ...core.TRACING_DEFAULTS,
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
  ...request.defaultRequestInstrumentationOptions
};
const browserTracingIntegration = ((options = {}) => {
  if ("enableElementTiming" in options) {
    core.consoleSandbox(() => {
      console.warn(
        "[Sentry] `enableElementTiming` is deprecated and no longer has any effect. Use the standalone `elementTimingIntegration` instead."
      );
    });
  }
  const optionalWindowDocument = helpers.WINDOW.document;
  const {
    // oxlint-disable-next-line typescript/no-deprecated -- still honoured until it is removed
    enableInp,
    enableLongTask,
    enableLongAnimationFrame,
    webVitals: webVitals$1,
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
  const _isBot = browserUtils.isBotUserAgent();
  let lastInteractionTimestamp;
  let _pageloadSpan;
  function _createRouteSpan(client, startSpanOptions, makeActive = true, url) {
    const isPageloadSpan = startSpanOptions.op === "pageload";
    const initialSpanName = startSpanOptions.name;
    const finalStartSpanOptions = beforeStartSpan ? beforeStartSpan(startSpanOptions) : startSpanOptions;
    const urlObject = core.parseStringToURLObject(url || browserUtils.getLocationHref());
    const attributes$1 = {
      ...urlObject?.pathname && { [attributes.URL_PATH]: urlObject.pathname },
      ...urlObject && !core.isURLObjectRelative(urlObject) && { [attributes.URL_FULL]: core.filterCollectedUrl(urlObject.href) },
      ...finalStartSpanOptions.attributes
    };
    if (initialSpanName !== finalStartSpanOptions.name) {
      attributes$1[attributes.SENTRY_SEGMENT_NAME_SOURCE] = "custom";
    }
    finalStartSpanOptions.attributes = attributes$1;
    if (!makeActive) {
      const now = core.dateTimestampInSeconds();
      browser.startInactiveSpan({
        ...finalStartSpanOptions,
        startTime: now
      }).end(now);
      return;
    }
    const idleSpan = browser.startIdleSpan(finalStartSpanOptions, {
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
        debugBuild.DEBUG_BUILD && core.debug.log("[Tracing] Skipping browserTracingIntegration setup for bot user agent.");
        return;
      }
      core.registerSpanErrorInstrumentation();
      if (enableLongAnimationFrame && core.GLOBAL_OBJ.PerformanceObserver && PerformanceObserver.supportedEntryTypes?.includes("long-animation-frame")) {
        browserUtils.startTrackingLongAnimationFrames();
      } else if (enableLongTask) {
        browserUtils.startTrackingLongTasks();
      }
      if (detectRedirects && optionalWindowDocument) {
        const interactionHandler = () => {
          lastInteractionTimestamp = core.timestampInSeconds();
        };
        addEventListener("click", interactionHandler, { capture: true });
        addEventListener("keydown", interactionHandler, { capture: true, passive: true });
      }
      function maybeEndActiveSpan() {
        const activeSpan = getActiveIdleSpan(client);
        if (activeSpan && !core.spanToJSON(activeSpan).end_timestamp) {
          debugBuild.DEBUG_BUILD && core.debug.log(
            `[Tracing] Finishing current active span with op: ${core.spanToJSON(activeSpan).attributes[attributes.SENTRY_OP]}`
          );
          activeSpan.setAttribute(attributes.SENTRY_IDLE_SPAN_FINISH_REASON, "cancelled");
          activeSpan.end();
        }
      }
      client.on("beforeIdleSpanEnd", (span) => {
        if (getActiveIdleSpan(client) !== span) {
          return;
        }
        browserUtils.addPerformanceEntries(span, {
          ignoreResourceSpans,
          spanStreamingEnabled: core.hasSpanStreamingEnabled(client)
        });
        setActiveIdleSpan(client, void 0);
        const scope = core.getCurrentScope();
        const oldPropagationContext = scope.getPropagationContext();
        scope.setPropagationContext({
          ...oldPropagationContext,
          traceId: span.spanContext().traceId,
          sampled: core.spanIsSampled(span),
          dsc: core.getDynamicSamplingContextFromSpan(span)
        });
        if (_pageloadSpan === span) {
          _pageloadSpan = void 0;
        }
      });
      client.on("startNavigationSpan", (startSpanOptions, navigationOptions) => {
        if (core.getClient() !== client) {
          return;
        }
        if (navigationOptions?.isRedirect) {
          debugBuild.DEBUG_BUILD && core.debug.warn("[Tracing] Detected redirect, navigation span will not be the root span, but a child span.");
          _createRouteSpan(
            client,
            {
              op: op.NAVIGATION_REDIRECT,
              ...startSpanOptions
            },
            false,
            navigationOptions.url
          );
          return;
        }
        lastInteractionTimestamp = void 0;
        maybeEndActiveSpan();
        const scope = core.getCurrentScope();
        scope.setPropagationContext({
          traceId: core.generateTraceId(),
          sampleRand: Math.random(),
          propagationSpanId: core.hasSpansEnabled() ? void 0 : core.generateSpanId()
        });
        scope.setSDKProcessingMetadata({
          normalizedRequest: void 0
        });
        _createRouteSpan(
          client,
          {
            op: op.NAVIGATION,
            ...startSpanOptions,
            // Navigation starts a new trace and is NOT parented under any active interaction (e.g. ui.action.click)
            parentSpan: null
          },
          true,
          navigationOptions?.url
        );
      });
      client.on("startPageLoadSpan", (startSpanOptions, traceOptions = {}) => {
        if (core.getClient() !== client) {
          return;
        }
        maybeEndActiveSpan();
        const sentryTrace = traceOptions.sentryTrace || getMetaContent("sentry-trace") || getServerTiming("sentry-trace");
        const baggage = traceOptions.baggage || getMetaContent("baggage") || getServerTiming("baggage");
        const propagationContext = core.propagationContextFromHeaders(sentryTrace, baggage);
        const scope = core.getCurrentScope();
        scope.setPropagationContext(propagationContext);
        if (!core.hasSpansEnabled()) {
          scope.getPropagationContext().propagationSpanId = core.generateSpanId();
        }
        scope.setSDKProcessingMetadata({
          normalizedRequest: helpers.getHttpRequestData()
        });
        _createRouteSpan(client, {
          op: op.PAGELOAD,
          ...startSpanOptions
        });
      });
      client.on("endPageloadSpan", () => {
        if (enableReportPageLoaded && _pageloadSpan) {
          _pageloadSpan.setAttribute(attributes.SENTRY_IDLE_SPAN_FINISH_REASON, "reportPageLoaded");
          _pageloadSpan.end();
        }
      });
      helpers.WINDOW.addEventListener?.("pagehide", () => {
        const activeSpan = getActiveIdleSpan(client);
        if (activeSpan && !core.spanToJSON(activeSpan).end_timestamp) {
          activeSpan.setAttribute(attributes.SENTRY_IDLE_SPAN_FINISH_REASON, "documentHidden");
          activeSpan.end();
        }
        void client.flush();
      });
    },
    afterAllSetup(client) {
      if (_isBot) {
        return;
      }
      browser._INTERNAL_ensureBrowserSpanStreaming(client);
      if (client.addIntegration && !client.getIntegrationByName?.(webVitals.WEB_VITALS_INTEGRATION_NAME)) {
        const ignore = webVitals$1?.ignore ?? [];
        client.addIntegration(
          webVitals.webVitalsIntegration({
            ...webVitals$1,
            ignore: enableInp || ignore.includes("inp") ? ignore : [...ignore, "inp"]
          })
        );
      }
      let startingUrl = browserUtils.getLocationHref();
      if (linkPreviousTrace !== "off") {
        linkedTraces.linkTraces(client, { linkPreviousTrace, consistentTraceSampling });
      }
      if (helpers.WINDOW.location) {
        if (instrumentPageLoad) {
          startBrowserTracingPageLoadSpan(client, {
            // With span streaming, span names have to be low cardinality, and there is no route
            // information available here.
            name: core.hasSpanStreamingEnabled(client) ? core.PAGELOAD_SPAN_NAME_FALLBACK : helpers.WINDOW.location.pathname,
            attributes: {
              [attributes.SENTRY_SEGMENT_NAME_SOURCE]: "url",
              [attributes.SENTRY_ORIGIN]: "auto.pageload.browser"
            }
          });
        }
        if (instrumentNavigation) {
          browserUtils.addHistoryInstrumentationHandler(({ to, from }) => {
            if (from === void 0 && startingUrl !== void 0 && startingUrl.indexOf(to) !== -1) {
              startingUrl = void 0;
              return;
            }
            startingUrl = void 0;
            const parsed = core.parseStringToURLObject(to);
            const activeSpan = getActiveIdleSpan(client);
            const navigationIsRedirect = activeSpan && detectRedirects && isRedirect(activeSpan, lastInteractionTimestamp);
            startBrowserTracingNavigationSpan(
              client,
              {
                // With span streaming, span names have to be low cardinality, and there is no route
                // information available here.
                name: core.hasSpanStreamingEnabled(client) ? core.NAVIGATION_SPAN_NAME_FALLBACK : parsed?.pathname || helpers.WINDOW.location.pathname,
                attributes: {
                  [attributes.SENTRY_SEGMENT_NAME_SOURCE]: "url",
                  [attributes.SENTRY_ORIGIN]: "auto.navigation.browser"
                }
              },
              { url: to, isRedirect: navigationIsRedirect }
            );
          });
        }
        if (instrumentBfcacheRestore) {
          helpers.WINDOW.addEventListener?.("pageshow", (event) => {
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
                name: core.hasSpanStreamingEnabled(client) ? core.NAVIGATION_SPAN_NAME_FALLBACK : helpers.WINDOW.location?.pathname || "/",
                attributes: {
                  [attributes.SENTRY_SEGMENT_NAME_SOURCE]: "url",
                  [attributes.SENTRY_ORIGIN]: "auto.navigation.browser.bfcache",
                  // A bfcache restore is near-instant, so these spans would otherwise drag
                  // navigation duration percentiles down with no way to tell them apart.
                  [attributes.BROWSER_NAVIGATION_TYPE]: "back-forward-cache"
                }
              },
              { url: helpers.WINDOW.location?.href }
            );
          });
        }
      }
      if (markBackgroundSpan) {
        backgroundtab.registerBackgroundTabDetection();
      }
      request.instrumentOutgoingRequests(client, {
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
  const isFallbackSpanName = spanOptions.name === core.PAGELOAD_SPAN_NAME_FALLBACK;
  core.getCurrentScope().setTransactionName(isFallbackSpanName ? helpers.WINDOW.location?.pathname : spanOptions.name);
  const timeOrigin = core.browserPerformanceTimeOrigin();
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
  const scope = core.getCurrentScope();
  const isFallbackSpanName = spanOptions.name === core.NAVIGATION_SPAN_NAME_FALLBACK;
  scope.setTransactionName(
    isFallbackSpanName ? url && core.parseStringToURLObject(url)?.pathname || helpers.WINDOW.location?.pathname : spanOptions.name
  );
  if (url && !isRedirect2) {
    scope.setSDKProcessingMetadata({
      normalizedRequest: {
        ...helpers.getHttpRequestData(),
        url
      }
    });
  }
  return getActiveIdleSpan(client);
}
function getMetaContent(metaName) {
  const optionalWindowDocument = helpers.WINDOW.document;
  const metaTag = optionalWindowDocument?.querySelector(`meta[name=${metaName}]`);
  return metaTag?.getAttribute("content") || void 0;
}
function getServerTiming(name) {
  const navigation = helpers.WINDOW.performance?.getEntriesByType?.("navigation")[0];
  const entry = navigation?.serverTiming?.find((entry2) => entry2.name === name);
  return entry?.description;
}
const ACTIVE_IDLE_SPAN_PROPERTY = "_sentry_idleSpan";
function getActiveIdleSpan(client) {
  return client[ACTIVE_IDLE_SPAN_PROPERTY];
}
function setActiveIdleSpan(client, span) {
  core.addNonEnumerableProperty(client, ACTIVE_IDLE_SPAN_PROPERTY, span);
}
const REDIRECT_THRESHOLD = 1.5;
function isRedirect(activeSpan, lastInteractionTimestamp) {
  const spanData = core.spanToJSON(activeSpan);
  const now = core.dateTimestampInSeconds();
  const startTimestamp = spanData.start_timestamp;
  if (now - startTimestamp > REDIRECT_THRESHOLD) {
    return false;
  }
  if (lastInteractionTimestamp && now - lastInteractionTimestamp <= REDIRECT_THRESHOLD) {
    return false;
  }
  return true;
}

exports.BROWSER_TRACING_INTEGRATION_ID = BROWSER_TRACING_INTEGRATION_ID;
exports.browserTracingIntegration = browserTracingIntegration;
exports.getMetaContent = getMetaContent;
exports.getServerTiming = getServerTiming;
exports.startBrowserTracingNavigationSpan = startBrowserTracingNavigationSpan;
exports.startBrowserTracingPageLoadSpan = startBrowserTracingPageLoadSpan;
//# sourceMappingURL=browserTracingIntegration.js.map
