Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const attributes = require('@sentry/conventions/attributes');
const core = require('@sentry/core');
const debugBuild = require('../debug-build.js');
const helpers = require('../helpers.js');

const INTEGRATION_NAME = "BfcacheMetrics";
const bfcacheMetricsIntegration = core.defineIntegration(
  (options = {}) => {
    const maxReasons = _resolveMaxReasons(options.maxReasons);
    return {
      name: INTEGRATION_NAME,
      setupOnce() {
        if (!helpers.WINDOW.addEventListener || !helpers.WINDOW.performance?.getEntriesByType) {
          debugBuild.DEBUG_BUILD && core.debug.log(`[${INTEGRATION_NAME}] Browser APIs unavailable, skipping instrumentation.`);
          return;
        }
        function onPageShow(event) {
          const routeName = _getSegmentName();
          if (event.persisted) {
            _captureBFCacheNavigation("hit", 0, routeName);
            return;
          }
          const navigationEntry = helpers.WINDOW.performance.getEntriesByType("navigation")[0];
          if (navigationEntry?.type !== "back_forward") {
            return;
          }
          const reasons = _collectNotRestoredReasons(navigationEntry.notRestoredReasons, maxReasons);
          _captureBFCacheNavigation("miss", reasons.length, routeName);
          if (typeof navigationEntry.duration === "number" && navigationEntry.duration > 0) {
            core.metrics.distribution("browser.bfcache.reload.duration", navigationEntry.duration, {
              unit: "millisecond",
              attributes: _withOriginAttr({
                [attributes.SENTRY_SEGMENT_NAME]: routeName
              })
            });
          }
          reasons.forEach((r) => _captureBFCacheReason(r, routeName));
        }
        helpers.WINDOW.addEventListener("pageshow", onPageShow, true);
      }
    };
  }
);
function _captureBFCacheNavigation(outcome, reasonCount, routeName) {
  core.metrics.count("browser.bfcache.navigation", 1, {
    attributes: _withOriginAttr({
      [attributes.BROWSER_BFCACHE_OUTCOME]: outcome,
      // Attribute should be present if reasons are >= 1
      [attributes.BROWSER_BFCACHE_NOT_RESTORED_REASON_COUNT]: reasonCount || void 0,
      [attributes.SENTRY_SEGMENT_NAME]: routeName
    })
  });
}
function _captureBFCacheReason({ reason, frame }, routeName) {
  core.metrics.count("browser.bfcache.not_restored", 1, {
    attributes: _withOriginAttr({
      [attributes.BROWSER_BFCACHE_REASON]: reason,
      [attributes.BROWSER_BFCACHE_FRAME]: frame,
      [attributes.SENTRY_SEGMENT_NAME]: routeName
    })
  });
}
function _getSegmentName() {
  return core.getCurrentScope().getScopeData().transactionName || helpers.WINDOW.location?.pathname;
}
function _resolveMaxReasons(maxReasons) {
  if (maxReasons == null) {
    return Infinity;
  }
  if (maxReasons < 1) {
    debugBuild.DEBUG_BUILD && core.debug.warn(`[${INTEGRATION_NAME}] \`maxReasons\` must be at least 1, got ${maxReasons}. Using 1 instead.`);
    return 1;
  }
  return maxReasons;
}
function _collectNotRestoredReasons(notRestoredReasons, maxReasons) {
  const reasons = [];
  if (!notRestoredReasons || maxReasons <= 0) {
    return reasons;
  }
  _collectReasonsFromFrame(notRestoredReasons, "top", reasons, maxReasons);
  return reasons;
}
function _collectReasonsFromFrame(frame, frameType, collectedReasons, maxReasons) {
  if (collectedReasons.length >= maxReasons) {
    return;
  }
  frame.reasons?.forEach((reason) => {
    if (collectedReasons.length >= maxReasons) {
      return;
    }
    const reasonValue = typeof reason === "string" ? reason : reason.reason;
    if (!reasonValue) {
      return;
    }
    collectedReasons.push({
      reason: reasonValue,
      frame: frameType
    });
  });
  frame.children?.forEach((child) => {
    _collectReasonsFromFrame(child, "child", collectedReasons, maxReasons);
  });
}
function _withOriginAttr(attributes$1) {
  attributes$1[attributes.SENTRY_ORIGIN] = "auto.browser.bfcache";
  return attributes$1;
}

exports._collectNotRestoredReasons = _collectNotRestoredReasons;
exports._resolveMaxReasons = _resolveMaxReasons;
exports.bfcacheMetricsIntegration = bfcacheMetricsIntegration;
//# sourceMappingURL=bfcacheMetrics.js.map
