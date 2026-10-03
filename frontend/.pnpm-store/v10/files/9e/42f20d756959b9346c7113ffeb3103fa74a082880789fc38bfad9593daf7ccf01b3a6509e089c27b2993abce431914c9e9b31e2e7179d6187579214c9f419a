import { defineIntegration, hasSpanStreamingEnabled } from '@sentry/core';
import { registerInpInteractionListener, supportsSoftNavigations, enableSoftNavigationReporting, startSoftNavigationCorrelation, enableBfcacheReporting, startTrackingWebVitals, addWebVitalsToSpan, trackLcpAsSpan, trackClsAsSpan, trackInpAsSpan } from '@sentry/browser-utils';

const WEB_VITALS_INTEGRATION_NAME = "WebVitals";
const webVitalsIntegration = defineIntegration((options = {}) => {
  const { ignore = [], softNavigations = true, bfcacheNavigations = true } = options;
  const ignored = new Set(ignore);
  return {
    name: WEB_VITALS_INTEGRATION_NAME,
    setup(client) {
      const spanStreamingEnabled = hasSpanStreamingEnabled(client);
      const reportSoftNavs = softNavigations && spanStreamingEnabled && supportsSoftNavigations();
      const reportBfcache = bfcacheNavigations && spanStreamingEnabled;
      const perNavigation = reportSoftNavs || reportBfcache;
      if (reportSoftNavs) {
        enableSoftNavigationReporting();
        startSoftNavigationCorrelation(client);
      }
      if (reportBfcache) {
        enableBfcacheReporting();
      }
      const trackClsOnPageloadSpan = !spanStreamingEnabled && !ignored.has("cls");
      const trackLcpOnPageloadSpan = !spanStreamingEnabled && !ignored.has("lcp");
      const finalizeWebVitals = startTrackingWebVitals({
        trackCls: trackClsOnPageloadSpan,
        trackLcp: trackLcpOnPageloadSpan,
        client
      });
      const pageloadSpans = /* @__PURE__ */ new WeakSet();
      client.on("afterStartPageLoadSpan", (span) => {
        pageloadSpans.add(span);
      });
      client.on("spanEnd", (span) => {
        if (!pageloadSpans.delete(span)) {
          return;
        }
        finalizeWebVitals();
        addWebVitalsToSpan(span, {
          recordClsOnPageloadSpan: trackClsOnPageloadSpan,
          recordLcpOnPageloadSpan: trackLcpOnPageloadSpan,
          spanStreamingEnabled
        });
      });
      if (spanStreamingEnabled) {
        if (!ignored.has("lcp")) {
          trackLcpAsSpan(client, perNavigation);
        }
        if (!ignored.has("cls")) {
          trackClsAsSpan(client, perNavigation);
        }
      }
      if (!ignored.has("inp")) {
        trackInpAsSpan(client, perNavigation);
      }
    },
    afterAllSetup() {
      if (!ignored.has("inp")) {
        registerInpInteractionListener();
      }
    }
  };
});

export { WEB_VITALS_INTEGRATION_NAME, webVitalsIntegration };
//# sourceMappingURL=webVitals.js.map
