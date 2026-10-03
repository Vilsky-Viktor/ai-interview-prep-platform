import { addFetchInstrumentationHandler, instrumentFetchRequest, parseUrl, stripDataUrlContent, filterCollectedUrl, spanToJSON, hasSpanStreamingEnabled, timestampInSeconds, hasSpansEnabled, setHttpStatus, stripUrlQueryAndFragment, getClient, getActiveSpan, getUrlDomain, getUrlFragment, filterCollectedUrlQuery, getUrlQuery, SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN, SentryNonRecordingSpan, spanIsIgnored, matchesTracePropagationTargets, getTraceData } from '@sentry/core';
import { startInactiveSpan } from '@sentry/core/browser';
import { addXhrInstrumentationHandler, addPerformanceInstrumentationHandler, resourceTimingToSpanAttributes, SENTRY_XHR_DATA_KEY, parseXhrResponseHeaders, getLocationHref } from '@sentry/browser-utils';
import { WINDOW } from '../helpers.js';
import { getFullURL, createHeadersSafely, isPerformanceResourceTiming, baggageHeaderHasSentryValues } from './utils.js';
import { SERVER_ADDRESS, URL_FULL, URL_FRAGMENT, URL_QUERY, SENTRY_OP, URL_DOMAIN, HTTP_REQUEST_METHOD } from '@sentry/conventions/attributes';
import { HTTP_CLIENT } from '@sentry/conventions/op';

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
    addFetchInstrumentationHandler((handlerData) => {
      const createdSpan = instrumentFetchRequest(handlerData, shouldCreateSpan, shouldAttachHeadersWithTargets, spans, {
        propagateTraceparent,
        onRequestSpanEnd,
        // The generic fetch instrumentation has no page origin to resolve relative URLs against.
        urlBase: WINDOW.location?.origin
      });
      if (createdSpan) {
        const fullUrl = getFullURL(handlerData.fetchData.url);
        const host = fullUrl ? parseUrl(fullUrl).host?.replace(/^.*@/, "") : void 0;
        const sanitizedFullUrl = fullUrl ? stripDataUrlContent(fullUrl) : void 0;
        createdSpan.setAttributes({
          [URL_FULL]: filterCollectedUrl(sanitizedFullUrl),
          [SERVER_ADDRESS]: host
        });
        if (enableHTTPTimings) {
          addHTTPTimings(createdSpan, client);
        }
        onRequestSpanStart?.(createdSpan, { headers: handlerData.headers });
      }
    });
  }
  if (traceXHR) {
    addXhrInstrumentationHandler((handlerData) => {
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
          headers: createHeadersSafely(handlerData.xhr.__sentry_xhr_v3__?.request_headers)
        });
      }
    });
  }
}
const HTTP_TIMING_WAIT_MS = 300;
function addHTTPTimings(span, client) {
  const url = spanToJSON(span).attributes[URL_FULL];
  if (!url || typeof url !== "string") {
    return;
  }
  let onEntryFound = () => void setTimeout(unsubscribePerformanceObsever);
  if (hasSpanStreamingEnabled(client)) {
    const originalEnd = span.end.bind(span);
    span.end = (endTimestamp) => {
      const capturedEndTimestamp = endTimestamp ?? timestampInSeconds();
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
  const unsubscribePerformanceObsever = addPerformanceInstrumentationHandler("resource", ({ entries }) => {
    entries.forEach((entry) => {
      if (isPerformanceResourceTiming(entry) && entry.name.endsWith(url)) {
        span.setAttributes(resourceTimingToSpanAttributes(entry));
        onEntryFound();
      }
    });
  });
}
function shouldAttachHeaders(targetUrl, tracePropagationTargets) {
  const href = getLocationHref();
  if (!href) {
    const isRelativeSameOriginRequest = !!targetUrl.match(/^\/(?!\/)/);
    if (!tracePropagationTargets) {
      return isRelativeSameOriginRequest;
    } else {
      return matchesTracePropagationTargets(targetUrl, tracePropagationTargets);
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
      return matchesTracePropagationTargets(resolvedUrl.toString(), tracePropagationTargets) || isSameOriginRequest && matchesTracePropagationTargets(resolvedUrl.pathname, tracePropagationTargets);
    }
  }
}
function xhrCallback(handlerData, shouldCreateSpan, shouldAttachHeaders2, spans, propagateTraceparent, onRequestSpanEnd) {
  const xhr = handlerData.xhr;
  const sentryXhrData = xhr?.[SENTRY_XHR_DATA_KEY];
  if (!xhr || xhr.__sentry_own_request__ || !sentryXhrData) {
    return void 0;
  }
  const { url, method } = sentryXhrData;
  const shouldCreateSpanResult = hasSpansEnabled() && shouldCreateSpan(url);
  if (handlerData.endTimestamp) {
    const spanId = xhr.__sentry_xhr_span_id__;
    if (!spanId) return;
    const span2 = spans[spanId];
    if (span2) {
      if (shouldCreateSpanResult && sentryXhrData.status_code !== void 0) {
        setHttpStatus(span2, sentryXhrData.status_code);
        span2.end();
        onRequestSpanEnd?.(span2, {
          headers: createHeadersSafely(parseXhrResponseHeaders(xhr)),
          error: handlerData.error
        });
      }
      delete spans[spanId];
    }
    return void 0;
  }
  const fullUrl = getFullURL(url);
  const parsedUrl = fullUrl ? parseUrl(fullUrl) : parseUrl(url);
  const sanitizedFullUrl = fullUrl ? stripDataUrlContent(fullUrl) : void 0;
  const urlForSpanName = stripDataUrlContent(stripUrlQueryAndFragment(url));
  const client = getClient();
  const hasParent = !!getActiveSpan();
  const shouldEmitSpan = hasParent || !!client && hasSpanStreamingEnabled(client);
  const host = parsedUrl?.host?.replace(/^.*@/, "");
  const domain = getUrlDomain(fullUrl || url);
  const streamedName = domain ? `${method} ${domain}` : method;
  const span = shouldCreateSpanResult && shouldEmitSpan ? startInactiveSpan({
    name: !!client && hasSpanStreamingEnabled(client) ? streamedName : `${method} ${urlForSpanName}`,
    attributes: {
      type: "xhr",
      // eslint-disable-next-line typescript/no-deprecated
      [HTTP_REQUEST_METHOD]: method,
      [URL_FULL]: filterCollectedUrl(sanitizedFullUrl),
      [SERVER_ADDRESS]: host,
      [URL_DOMAIN]: domain,
      [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.http.browser",
      [SENTRY_OP]: HTTP_CLIENT,
      [URL_QUERY]: filterCollectedUrlQuery(getUrlQuery(parsedUrl?.search)),
      [URL_FRAGMENT]: getUrlFragment(parsedUrl?.hash)
    }
  }) : new SentryNonRecordingSpan();
  const spanForTraceHeaders = spanIsIgnored(span) && hasParent ? void 0 : span;
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
      hasSpansEnabled() && shouldEmitSpan ? spanForTraceHeaders : void 0,
      propagateTraceparent
    );
  }
  if (client) {
    client.emit("beforeOutgoingRequestSpan", span, handlerData);
  }
  return span;
}
function addTracingHeadersToXhrRequest(xhr, span, propagateTraceparent) {
  const { "sentry-trace": sentryTrace, baggage, traceparent } = getTraceData({ span, propagateTraceparent });
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
      if (!originalBaggageHeader || !baggageHeaderHasSentryValues(originalBaggageHeader)) {
        xhr.setRequestHeader("baggage", sentryBaggageHeader);
      }
    }
  } catch {
  }
}

export { defaultRequestInstrumentationOptions, instrumentOutgoingRequests, shouldAttachHeaders };
//# sourceMappingURL=request.js.map
