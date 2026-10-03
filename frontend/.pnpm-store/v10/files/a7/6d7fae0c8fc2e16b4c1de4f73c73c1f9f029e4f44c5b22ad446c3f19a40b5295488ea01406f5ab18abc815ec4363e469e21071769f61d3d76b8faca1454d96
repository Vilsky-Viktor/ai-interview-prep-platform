Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const attributes = require('@sentry/conventions/attributes');
const op = require('@sentry/conventions/op');
const core = require('@sentry/core');
const browser = require('@sentry/core/browser');
const helpers = require('../helpers.js');

const responseToStreamSpan = /* @__PURE__ */ new WeakMap();
const responseToFallbackTimeout = /* @__PURE__ */ new WeakMap();
const STREAM_RESOLVE_FALLBACK_MS = 9e4;
const STREAMING_CONTENT_TYPES = ["text/event-stream", "application/x-ndjson", "application/stream+json"];
const fetchStreamPerformanceIntegration = core.defineIntegration(() => {
  return {
    name: "FetchStreamPerformance",
    setup(client) {
      core.addFetchEndInstrumentationHandler((handlerData) => {
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
      core.addFetchInstrumentationHandler((handlerData) => {
        if (handlerData.endTimestamp && handlerData.response) {
          const contentType = handlerData.response.headers?.get("content-type") || "";
          if (handlerData.response.headers?.get("content-length") || !STREAMING_CONTENT_TYPES.some((t) => contentType.startsWith(t))) {
            return;
          }
          const url = handlerData.fetchData?.url || "";
          const method = handlerData.fetchData?.method || "GET";
          const parsedUrl = core.parseStringToURLObject(url);
          const sanitizedUrl = url.startsWith("data:") ? core.stripDataUrlContent(url) : parsedUrl ? core.getSanitizedUrlStringFromUrlObject(parsedUrl) : url;
          const domain = core.getUrlDomain(url, helpers.WINDOW.location?.origin);
          const streamedName = domain ? `${method} ${domain}` : method;
          const streamSpan = browser.startInactiveSpan({
            name: core.hasSpanStreamingEnabled(client) ? streamedName : `${method} ${sanitizedUrl}`,
            startTime: handlerData.endTimestamp,
            attributes: {
              [attributes.URL_FULL]: core.filterCollectedUrl(core.stripDataUrlContent(url)),
              [attributes.URL_DOMAIN]: domain,
              [attributes.HTTP_REQUEST_METHOD]: method,
              type: "fetch",
              [attributes.SENTRY_OP]: op.HTTP_CLIENT_STREAM,
              [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.http.browser.stream"
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

exports.fetchStreamPerformanceIntegration = fetchStreamPerformanceIntegration;
//# sourceMappingURL=fetchStreamPerformance.js.map
