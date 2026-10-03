Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const helpers = require('../helpers.js');
const attributes = require('@sentry/conventions/attributes');

const httpContextIntegration = core.defineIntegration(() => {
  return {
    name: "HttpContext",
    preprocessEvent(event, _hint, client) {
      if (!helpers.WINDOW.navigator && !helpers.WINDOW.location && !helpers.WINDOW.document) {
        return;
      }
      const { url, headers: collectedHeaders } = helpers.getHttpRequestData();
      const behavior = client.getDataCollectionOptions().httpHeaders.request;
      const userHeaders = Object.entries(event.request?.headers ?? {}).filter(([key]) => !(key in collectedHeaders));
      const headers = {
        ...core._INTERNAL_filterKeyValueData(collectedHeaders, behavior),
        ...Object.fromEntries(userHeaders)
      };
      event.request = {
        // The URL isn't gated by `dataCollection`, same as on the server.
        url,
        ...event.request,
        ...Object.keys(headers).length > 0 ? { headers } : { headers: void 0 }
      };
    },
    processSpan(span, client) {
      if (!helpers.WINDOW.navigator && !helpers.WINDOW.location && !helpers.WINDOW.document) {
        return;
      }
      const reqData = helpers.getHttpRequestData();
      const headers = core._INTERNAL_filterKeyValueData(
        reqData.headers,
        client.getDataCollectionOptions().httpHeaders.request
      );
      const referer = headers["Referer"];
      const { hostname, protocol } = helpers.WINDOW.location || {};
      core.safeSetSpanJSONAttributes(span, {
        // This attribute is used by the "Filter out events from legacy browsers and crawlers" features on the Sentry backend.
        // Therefore, it's set on every span.
        [attributes.USER_AGENT_ORIGINAL]: headers["User-Agent"],
        // Likewise for the "Filter out localhost events" feature. Deliberately inlined rather than
        // sharing the server-side helper, which costs bundle size for request headers and IPs that
        // don't exist here. Mirrors Relay's localhost filter (relay-filter/src/localhost.rs).
        [attributes.SENTRY_IS_LOCALHOST]: protocol === "file:" || hostname === "localhost" || hostname === "127.0.0.1" || // `location.hostname` keeps the brackets for IPv6 hosts, so this is `[::1]`, not `::1`.
        hostname === "[::1]" || !!hostname?.endsWith(".localhost"),
        // These attributes, we only need on the segment span (analogous to the `request` context for events)
        ...span.is_segment && {
          // Coerce empty string to undefined so the helper's nullish check drops it,
          // rather than writing an empty `url.full` attribute onto the span.
          [attributes.URL_FULL]: span.attributes?.[attributes.SENTRY_OP] !== "http.client" ? core.filterCollectedUrl(reqData.url) : void 0,
          [`${attributes.HTTP_REQUEST_HEADER_KEY_BASE}.referer`]: referer ? [referer] : void 0
        }
      });
    }
  };
});

exports.httpContextIntegration = httpContextIntegration;
//# sourceMappingURL=httpcontext.js.map
