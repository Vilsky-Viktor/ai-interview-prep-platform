Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const browserUtils = require('@sentry/browser-utils');

const WEB_VITALS_INTEGRATION_NAME = "WebVitals";
const webVitalsIntegration = core.defineIntegration((options = {}) => {
  const { ignore = [], softNavigations = true, bfcacheNavigations = true } = options;
  const ignored = new Set(ignore);
  return {
    name: WEB_VITALS_INTEGRATION_NAME,
    setup(client) {
      const spanStreamingEnabled = core.hasSpanStreamingEnabled(client);
      const reportSoftNavs = softNavigations && spanStreamingEnabled && browserUtils.supportsSoftNavigations();
      const reportBfcache = bfcacheNavigations && spanStreamingEnabled;
      const perNavigation = reportSoftNavs || reportBfcache;
      if (reportSoftNavs) {
        browserUtils.enableSoftNavigationReporting();
        browserUtils.startSoftNavigationCorrelation(client);
      }
      if (reportBfcache) {
        browserUtils.enableBfcacheReporting();
      }
      const trackClsOnPageloadSpan = !spanStreamingEnabled && !ignored.has("cls");
      const trackLcpOnPageloadSpan = !spanStreamingEnabled && !ignored.has("lcp");
      const finalizeWebVitals = browserUtils.startTrackingWebVitals({
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
        browserUtils.addWebVitalsToSpan(span, {
          recordClsOnPageloadSpan: trackClsOnPageloadSpan,
          recordLcpOnPageloadSpan: trackLcpOnPageloadSpan,
          spanStreamingEnabled
        });
      });
      if (spanStreamingEnabled) {
        if (!ignored.has("lcp")) {
          browserUtils.trackLcpAsSpan(client, perNavigation);
        }
        if (!ignored.has("cls")) {
          browserUtils.trackClsAsSpan(client, perNavigation);
        }
      }
      if (!ignored.has("inp")) {
        browserUtils.trackInpAsSpan(client, perNavigation);
      }
    },
    afterAllSetup() {
      if (!ignored.has("inp")) {
        browserUtils.registerInpInteractionListener();
      }
    }
  };
});

exports.WEB_VITALS_INTEGRATION_NAME = WEB_VITALS_INTEGRATION_NAME;
exports.webVitalsIntegration = webVitalsIntegration;
//# sourceMappingURL=webVitals.js.map
