import { SENTRY_ORIGIN, SENTRY_SEGMENT_NAME, BROWSER_BFCACHE_FRAME, BROWSER_BFCACHE_REASON, BROWSER_BFCACHE_NOT_RESTORED_REASON_COUNT, BROWSER_BFCACHE_OUTCOME } from '@sentry/conventions/attributes';
import { defineIntegration, debug, metrics, getCurrentScope } from '@sentry/core';
import { DEBUG_BUILD } from '../debug-build.js';
import { WINDOW } from '../helpers.js';

const INTEGRATION_NAME = "BfcacheMetrics";
const bfcacheMetricsIntegration = defineIntegration(
  (options = {}) => {
    const maxReasons = _resolveMaxReasons(options.maxReasons);
    return {
      name: INTEGRATION_NAME,
      setupOnce() {
        if (!WINDOW.addEventListener || !WINDOW.performance?.getEntriesByType) {
          DEBUG_BUILD && debug.log(`[${INTEGRATION_NAME}] Browser APIs unavailable, skipping instrumentation.`);
          return;
        }
        function onPageShow(event) {
          const routeName = _getSegmentName();
          if (event.persisted) {
            _captureBFCacheNavigation("hit", 0, routeName);
            return;
          }
          const navigationEntry = WINDOW.performance.getEntriesByType("navigation")[0];
          if (navigationEntry?.type !== "back_forward") {
            return;
          }
          const reasons = _collectNotRestoredReasons(navigationEntry.notRestoredReasons, maxReasons);
          _captureBFCacheNavigation("miss", reasons.length, routeName);
          if (typeof navigationEntry.duration === "number" && navigationEntry.duration > 0) {
            metrics.distribution("browser.bfcache.reload.duration", navigationEntry.duration, {
              unit: "millisecond",
              attributes: _withOriginAttr({
                [SENTRY_SEGMENT_NAME]: routeName
              })
            });
          }
          reasons.forEach((r) => _captureBFCacheReason(r, routeName));
        }
        WINDOW.addEventListener("pageshow", onPageShow, true);
      }
    };
  }
);
function _captureBFCacheNavigation(outcome, reasonCount, routeName) {
  metrics.count("browser.bfcache.navigation", 1, {
    attributes: _withOriginAttr({
      [BROWSER_BFCACHE_OUTCOME]: outcome,
      // Attribute should be present if reasons are >= 1
      [BROWSER_BFCACHE_NOT_RESTORED_REASON_COUNT]: reasonCount || void 0,
      [SENTRY_SEGMENT_NAME]: routeName
    })
  });
}
function _captureBFCacheReason({ reason, frame }, routeName) {
  metrics.count("browser.bfcache.not_restored", 1, {
    attributes: _withOriginAttr({
      [BROWSER_BFCACHE_REASON]: reason,
      [BROWSER_BFCACHE_FRAME]: frame,
      [SENTRY_SEGMENT_NAME]: routeName
    })
  });
}
function _getSegmentName() {
  return getCurrentScope().getScopeData().transactionName || WINDOW.location?.pathname;
}
function _resolveMaxReasons(maxReasons) {
  if (maxReasons == null) {
    return Infinity;
  }
  if (maxReasons < 1) {
    DEBUG_BUILD && debug.warn(`[${INTEGRATION_NAME}] \`maxReasons\` must be at least 1, got ${maxReasons}. Using 1 instead.`);
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
function _withOriginAttr(attributes) {
  attributes[SENTRY_ORIGIN] = "auto.browser.bfcache";
  return attributes;
}

export { _collectNotRestoredReasons, _resolveMaxReasons, bfcacheMetricsIntegration };
//# sourceMappingURL=bfcacheMetrics.js.map
