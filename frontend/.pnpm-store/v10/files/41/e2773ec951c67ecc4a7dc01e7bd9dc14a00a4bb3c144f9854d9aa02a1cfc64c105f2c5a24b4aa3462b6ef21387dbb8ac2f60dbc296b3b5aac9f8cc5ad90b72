import { defineIntegration, _INTERNAL_filterKeyValueData, safeSetSpanJSONAttributes, filterCollectedUrl } from '@sentry/core';
import { WINDOW, getHttpRequestData } from '../helpers.js';
import { HTTP_REQUEST_HEADER_KEY_BASE, URL_FULL, SENTRY_OP, SENTRY_IS_LOCALHOST, USER_AGENT_ORIGINAL } from '@sentry/conventions/attributes';

const httpContextIntegration = defineIntegration(() => {
  return {
    name: "HttpContext",
    preprocessEvent(event, _hint, client) {
      if (!WINDOW.navigator && !WINDOW.location && !WINDOW.document) {
        return;
      }
      const { url, headers: collectedHeaders } = getHttpRequestData();
      const behavior = client.getDataCollectionOptions().httpHeaders.request;
      const userHeaders = Object.entries(event.request?.headers ?? {}).filter(([key]) => !(key in collectedHeaders));
      const headers = {
        ..._INTERNAL_filterKeyValueData(collectedHeaders, behavior),
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
      if (!WINDOW.navigator && !WINDOW.location && !WINDOW.document) {
        return;
      }
      const reqData = getHttpRequestData();
      const headers = _INTERNAL_filterKeyValueData(
        reqData.headers,
        client.getDataCollectionOptions().httpHeaders.request
      );
      const referer = headers["Referer"];
      const { hostname, protocol } = WINDOW.location || {};
      safeSetSpanJSONAttributes(span, {
        // This attribute is used by the "Filter out events from legacy browsers and crawlers" features on the Sentry backend.
        // Therefore, it's set on every span.
        [USER_AGENT_ORIGINAL]: headers["User-Agent"],
        // Likewise for the "Filter out localhost events" feature. Deliberately inlined rather than
        // sharing the server-side helper, which costs bundle size for request headers and IPs that
        // don't exist here. Mirrors Relay's localhost filter (relay-filter/src/localhost.rs).
        [SENTRY_IS_LOCALHOST]: protocol === "file:" || hostname === "localhost" || hostname === "127.0.0.1" || // `location.hostname` keeps the brackets for IPv6 hosts, so this is `[::1]`, not `::1`.
        hostname === "[::1]" || !!hostname?.endsWith(".localhost"),
        // These attributes, we only need on the segment span (analogous to the `request` context for events)
        ...span.is_segment && {
          // Coerce empty string to undefined so the helper's nullish check drops it,
          // rather than writing an empty `url.full` attribute onto the span.
          [URL_FULL]: span.attributes?.[SENTRY_OP] !== "http.client" ? filterCollectedUrl(reqData.url) : void 0,
          [`${HTTP_REQUEST_HEADER_KEY_BASE}.referer`]: referer ? [referer] : void 0
        }
      });
    }
  };
});

export { httpContextIntegration };
//# sourceMappingURL=httpcontext.js.map
