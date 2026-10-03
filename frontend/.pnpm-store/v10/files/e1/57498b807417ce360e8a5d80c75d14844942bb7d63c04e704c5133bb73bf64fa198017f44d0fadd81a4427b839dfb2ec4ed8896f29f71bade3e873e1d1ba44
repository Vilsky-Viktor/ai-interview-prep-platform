import { SENTRY_OP, HTTP_REQUEST_METHOD, URL_DOMAIN, URL_FULL } from '@sentry/conventions/attributes';
import { HTTP_CLIENT_STREAM } from '@sentry/conventions/op';
import { defineIntegration, addFetchEndInstrumentationHandler, addFetchInstrumentationHandler, parseStringToURLObject, stripDataUrlContent, getSanitizedUrlStringFromUrlObject, getUrlDomain, SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN, filterCollectedUrl, hasSpanStreamingEnabled } from '@sentry/core';
import { startInactiveSpan } from '@sentry/core/browser';
import { WINDOW } from '../helpers.js';

const responseToStreamSpan = /* @__PURE__ */ new WeakMap();
const responseToFallbackTimeout = /* @__PURE__ */ new WeakMap();
const STREAM_RESOLVE_FALLBACK_MS = 9e4;
const STREAMING_CONTENT_TYPES = ["text/event-stream", "application/x-ndjson", "application/stream+json"];
const fetchStreamPerformanceIntegration = defineIntegration(() => {
  return {
    name: "FetchStreamPerformance",
    setup(client) {
      addFetchEndInstrumentationHandler((handlerData) => {
        if (handlerData.response) {
          const streamSpan = responseToStreamSpan.get(handlerData.response);
          if (streamSpan && handlerData.endTimestamp) {
            streamSpan.end(handlerData.endTimestamp);
            const fallbackTimeout = responseToFallbackTimeout.get(handlerData.response);
            if (fallbackTimeout) {
              clearTimeout(fallbackTimeout);
            }
          }
        }
      });
      addFetchInstrumentationHandler((handlerData) => {
        if (handlerData.endTimestamp && handlerData.response) {
          const contentType = handlerData.response.headers?.get("content-type") || "";
          if (handlerData.response.headers?.get("content-length") || !STREAMING_CONTENT_TYPES.some((t) => contentType.startsWith(t))) {
            return;
          }
          const url = handlerData.fetchData?.url || "";
          const method = handlerData.fetchData?.method || "GET";
          const parsedUrl = parseStringToURLObject(url);
          const sanitizedUrl = url.startsWith("data:") ? stripDataUrlContent(url) : parsedUrl ? getSanitizedUrlStringFromUrlObject(parsedUrl) : url;
          const domain = getUrlDomain(url, WINDOW.location?.origin);
          const streamedName = domain ? `${method} ${domain}` : method;
          const streamSpan = startInactiveSpan({
            name: hasSpanStreamingEnabled(client) ? streamedName : `${method} ${sanitizedUrl}`,
            startTime: handlerData.endTimestamp,
            attributes: {
              [URL_FULL]: filterCollectedUrl(stripDataUrlContent(url)),
              [URL_DOMAIN]: domain,
              [HTTP_REQUEST_METHOD]: method,
              type: "fetch",
              [SENTRY_OP]: HTTP_CLIENT_STREAM,
              [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.http.browser.stream"
            }
          });
          responseToStreamSpan.set(handlerData.response, streamSpan);
          const fallbackTimeout = setTimeout(() => {
            if (streamSpan.isRecording()) {
              streamSpan.end();
            }
          }, STREAM_RESOLVE_FALLBACK_MS);
          responseToFallbackTimeout.set(handlerData.response, fallbackTimeout);
        }
      });
    }
  };
});

export { fetchStreamPerformanceIntegration };
//# sourceMappingURL=fetchStreamPerformance.js.map
