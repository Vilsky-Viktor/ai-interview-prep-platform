Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const browser = require('@sentry/core/browser');
const browserUtils = require('@sentry/browser-utils');
const helpers = require('../helpers.js');
const utils = require('./utils.js');
const attributes = require('@sentry/conventions/attributes');
const op = require('@sentry/conventions/op');

const defaultRequestInstrumentationOptions = {
  traceFetch: true,
  traceXHR: true,
  enableHTTPTimings: true
};
function instrumentOutgoingRequests(client, _options) {
  const {
    traceFetch,
    traceXHR,
    shouldCreateSpanForRequest,
    enableHTTPTimings,
    tracePropagationTargets,
    onRequestSpanStart,
    onRequestSpanEnd
  } = {
    ...defaultRequestInstrumentationOptions,
    ..._options
  };
  const shouldCreateSpan = typeof shouldCreateSpanForRequest === "function" ? shouldCreateSpanForRequest : (_) => true;
  const shouldAttachHeadersWithTargets = (url) => shouldAttachHeaders(url, tracePropagationTargets);
  const spans = {};
  const propagateTraceparent = client.getOptions().propagateTraceparent;
  if (traceFetch) {
    core.addFetchInstrumentationHandler((handlerData) => {
      const createdSpan = core.instrumentFetchRequest(handlerData, shouldCreateSpan, shouldAttachHeadersWithTargets, spans, {
        propagateTraceparent,
        onRequestSpanEnd,
        // The generic fetch instrumentation has no page origin to resolve relative URLs against.
        urlBase: helpers.WINDOW.location?.origin
      });
      if (createdSpan) {
        const fullUrl = utils.getFullURL(handlerData.fetchData.url);
        const host = fullUrl ? core.parseUrl(fullUrl).host?.replace(/^.*@/, "") : void 0;
        const sanitizedFullUrl = fullUrl ? core.stripDataUrlContent(fullUrl) : void 0;
        createdSpan.setAttributes({
          [attributes.URL_FULL]: core.filterCollectedUrl(sanitizedFullUrl),
          [attributes.SERVER_ADDRESS]: host
        });
        if (enableHTTPTimings) {
          addHTTPTimings(createdSpan, client);
        }
        onRequestSpanStart?.(createdSpan, { headers: handlerData.headers });
      }
    });
  }
  if (traceXHR) {
    browserUtils.addXhrInstrumentationHandler((handlerData) => {
      const createdSpan = xhrCallback(
        handlerData,
        shouldCreateSpan,
        shouldAttachHeadersWithTargets,
        spans,
        propagateTraceparent,
        onRequestSpanEnd
      );
      if (createdSpan) {
        if (enableHTTPTimings) {
          addHTTPTimings(createdSpan, client);
        }
        onRequestSpanStart?.(createdSpan, {
          headers: utils.createHeadersSafely(handlerData.xhr.__sentry_xhr_v3__?.request_headers)
        });
      }
    });
  }
}
const HTTP_TIMING_WAIT_MS = 300;
function addHTTPTimings(span, client) {
  const url = core.spanToJSON(span).attributes[attributes.URL_FULL];
  if (!url || typeof url !== "string") {
    return;
  }
  let onEntryFound = () => void setTimeout(unsubscribePerformanceObsever);
  if (core.hasSpanStreamingEnabled(client)) {
    const originalEnd = span.end.bind(span);
    span.end = (endTimestamp) => {
      const capturedEndTimestamp = endTimestamp ?? core.timestampInSeconds();
      let isEnded = false;
      const endSpanAndCleanup = () => {
        if (isEnded) {
          return;
        }
        isEnded = true;
        setTimeout(unsubscribePerformanceObsever);
        originalEnd(capturedEndTimestamp);
        clearTimeout(fallbackTimeout);
      };
      onEntryFound = endSpanAndCleanup;
      const fallbackTimeout = setTimeout(endSpanAndCleanup, HTTP_TIMING_WAIT_MS);
    };
  }
  const unsubscribePerformanceObsever = browserUtils.addPerformanceInstrumentationHandler("resource", ({ entries }) => {
    entries.forEach((entry) => {
      if (utils.isPerformanceResourceTiming(entry) && entry.name.endsWith(url)) {
        span.setAttributes(browserUtils.resourceTimingToSpanAttributes(entry));
        onEntryFound();
      }
    });
  });
}
function shouldAttachHeaders(targetUrl, tracePropagationTargets) {
  const href = browserUtils.getLocationHref();
  if (!href) {
    const isRelativeSameOriginRequest = !!targetUrl.match(/^\/(?!\/)/);
    if (!tracePropagationTargets) {
      return isRelativeSameOriginRequest;
    } else {
      return core.matchesTracePropagationTargets(targetUrl, tracePropagationTargets);
    }
  } else {
    let resolvedUrl;
    let currentOrigin;
    try {
      resolvedUrl = new URL(targetUrl, href);
      currentOrigin = new URL(href).origin;
    } catch {
      return false;
    }
    const isSameOriginRequest = resolvedUrl.origin === currentOrigin;
    if (!tracePropagationTargets) {
      return isSameOriginRequest;
    } else {
      return core.matchesTracePropagationTargets(resolvedUrl.toString(), tracePropagationTargets) || isSameOriginRequest && core.matchesTracePropagationTargets(resolvedUrl.pathname, tracePropagationTargets);
    }
  }
}
function xhrCallback(handlerData, shouldCreateSpan, shouldAttachHeaders2, spans, propagateTraceparent, onRequestSpanEnd) {
  const xhr = handlerData.xhr;
  const sentryXhrData = xhr?.[browserUtils.SENTRY_XHR_DATA_KEY];
  if (!xhr || xhr.__sentry_own_request__ || !sentryXhrData) {
    return void 0;
  }
  const { url, method } = sentryXhrData;
  const shouldCreateSpanResult = core.hasSpansEnabled() && shouldCreateSpan(url);
  if (handlerData.endTimestamp) {
    const spanId = xhr.__sentry_xhr_span_id__;
    if (!spanId) return;
    const span2 = spans[spanId];
    if (span2) {
      if (shouldCreateSpanResult && sentryXhrData.status_code !== void 0) {
        core.setHttpStatus(span2, sentryXhrData.status_code);
        span2.end();
        onRequestSpanEnd?.(span2, {
          headers: utils.createHeadersSafely(browserUtils.parseXhrResponseHeaders(xhr)),
          error: handlerData.error
        });
      }
      delete spans[spanId];
    }
    return void 0;
  }
  const fullUrl = utils.getFullURL(url);
  const parsedUrl = fullUrl ? core.parseUrl(fullUrl) : core.parseUrl(url);
  const sanitizedFullUrl = fullUrl ? core.stripDataUrlContent(fullUrl) : void 0;
  const urlForSpanName = core.stripDataUrlContent(core.stripUrlQueryAndFragment(url));
  const client = core.getClient();
  const hasParent = !!core.getActiveSpan();
  const shouldEmitSpan = hasParent || !!client && core.hasSpanStreamingEnabled(client);
  const host = parsedUrl?.host?.replace(/^.*@/, "");
  const domain = core.getUrlDomain(fullUrl || url);
  const streamedName = domain ? `${method} ${domain}` : method;
  const span = shouldCreateSpanResult && shouldEmitSpan ? browser.startInactiveSpan({
    name: !!client && core.hasSpanStreamingEnabled(client) ? streamedName : `${method} ${urlForSpanName}`,
    attributes: {
      type: "xhr",
      // eslint-disable-next-line typescript/no-deprecated
      [attributes.HTTP_REQUEST_METHOD]: method,
      [attributes.URL_FULL]: core.filterCollectedUrl(sanitizedFullUrl),
      [attributes.SERVER_ADDRESS]: host,
      [attributes.URL_DOMAIN]: domain,
      [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.http.browser",
      [attributes.SENTRY_OP]: op.HTTP_CLIENT,
      [attributes.URL_QUERY]: core.filterCollectedUrlQuery(core.getUrlQuery(parsedUrl?.search)),
      [attributes.URL_FRAGMENT]: core.getUrlFragment(parsedUrl?.hash)
    }
  }) : new core.SentryNonRecordingSpan();
  const spanForTraceHeaders = core.spanIsIgnored(span) && hasParent ? void 0 : span;
  if (shouldCreateSpanResult && !shouldEmitSpan) {
    client?.recordDroppedEvent("no_parent_span", "span");
  }
  xhr.__sentry_xhr_span_id__ = span.spanContext().spanId;
  spans[xhr.__sentry_xhr_span_id__] = span;
  if (shouldAttachHeaders2(url)) {
    addTracingHeadersToXhrRequest(
      xhr,
      // If performance is disabled (TWP) or there's no active root span (pageload/navigation/interaction),
      // we do not want to use the span as base for the trace headers,
      // which means that the headers will be generated from the scope and the sampling decision is deferred
      core.hasSpansEnabled() && shouldEmitSpan ? spanForTraceHeaders : void 0,
      propagateTraceparent
    );
  }
  if (client) {
    client.emit("beforeOutgoingRequestSpan", span, handlerData);
  }
  return span;
}
function addTracingHeadersToXhrRequest(xhr, span, propagateTraceparent) {
  const { "sentry-trace": sentryTrace, baggage, traceparent } = core.getTraceData({ span, propagateTraceparent });
  if (sentryTrace) {
    setHeaderOnXhr(xhr, sentryTrace, baggage, traceparent);
  }
}
function setHeaderOnXhr(xhr, sentryTraceHeader, sentryBaggageHeader, traceparentHeader) {
  const originalHeaders = xhr.__sentry_xhr_v3__?.request_headers;
  if (originalHeaders?.["sentry-trace"] || !xhr.setRequestHeader) {
    return;
  }
  try {
    xhr.setRequestHeader("sentry-trace", sentryTraceHeader);
    if (traceparentHeader && !originalHeaders?.["traceparent"]) {
      xhr.setRequestHeader("traceparent", traceparentHeader);
    }
    if (sentryBaggageHeader) {
      const originalBaggageHeader = originalHeaders?.["baggage"];
      if (!originalBaggageHeader || !utils.baggageHeaderHasSentryValues(originalBaggageHeader)) {
        xhr.setRequestHeader("baggage", sentryBaggageHeader);
      }
    }
  } catch {
  }
}

exports.defaultRequestInstrumentationOptions = defaultRequestInstrumentationOptions;
exports.instrumentOutgoingRequests = instrumentOutgoingRequests;
exports.shouldAttachHeaders = shouldAttachHeaders;
//# sourceMappingURL=request.js.map
