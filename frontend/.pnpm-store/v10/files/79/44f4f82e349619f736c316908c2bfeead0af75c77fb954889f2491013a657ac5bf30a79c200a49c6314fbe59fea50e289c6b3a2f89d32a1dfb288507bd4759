Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const attributes = require('@sentry/conventions/attributes');
const core = require('@sentry/core');
const utils = require('./utils.js');
const utils$1 = require('../web-vitals/utils.js');

const INTEGRATION_NAME = "UserTiming";
const _userTimingIntegration = ((options = {}) => {
  return {
    name: INTEGRATION_NAME,
    setup(client) {
      const performance = utils.getBrowserPerformanceAPI();
      const timeOrigin = core.browserPerformanceTimeOrigin();
      if (!performance?.getEntries || !timeOrigin) {
        return;
      }
      const timeOriginInSeconds = utils.msToSec(timeOrigin);
      let performanceCursor = 0;
      client.on("beforeIdleSpanEnd", (idleSpan) => {
        const { attributes: attributes$1, start_timestamp: parentStartTimestamp } = core.spanToJSON(idleSpan);
        const parentOp = attributes$1[attributes.SENTRY_OP];
        if (parentOp !== "pageload" && parentOp !== "navigation") {
          return;
        }
        const requestTime = utils.msToSec(utils$1.getNavigationEntry(false)?.requestStart ?? 0);
        const performanceEntries = performance.getEntries();
        for (const entry of performanceEntries.slice(performanceCursor)) {
          if (entry.entryType !== "mark" && entry.entryType !== "measure") {
            continue;
          }
          const startTime = utils.msToSec(entry.startTime);
          const absoluteStartTime = timeOriginInSeconds + startTime;
          if (parentOp === "navigation" && parentStartTimestamp && absoluteStartTime < parentStartTimestamp) {
            continue;
          }
          _addUserTimingSpan(
            idleSpan,
            entry,
            startTime,
            utils.msToSec(Math.max(0, entry.duration)),
            timeOriginInSeconds,
            requestTime,
            options.ignore ?? []
          );
        }
        performanceCursor = performanceEntries.length;
      });
    }
  };
});
const userTimingIntegration = core.defineIntegration(_userTimingIntegration);
function _addUserTimingSpan(parentSpan, entry, startTime, duration, timeOrigin, requestTime, ignore) {
  if (isReact19MeasureEntry(entry) || core.stringMatchesSomePattern(entry.name, ignore)) {
    return;
  }
  const spanStartTimestamp = timeOrigin + Math.max(startTime, requestTime);
  const originalStartTimestamp = timeOrigin + startTime;
  const spanEndTimestamp = originalStartTimestamp + duration;
  const attributes$1 = {
    [attributes.SENTRY_ORIGIN]: `auto.browser.user_timing.${entry.entryType}`
  };
  if (spanStartTimestamp !== originalStartTimestamp) {
    attributes$1["sentry.browser.measure_happened_before_request"] = true;
    attributes$1["sentry.browser.measure_start_time"] = spanStartTimestamp;
  }
  addDetailToSpanAttributes(attributes$1, entry);
  if (spanStartTimestamp <= spanEndTimestamp) {
    utils.startAndEndSpan(parentSpan, spanStartTimestamp, spanEndTimestamp, {
      name: entry.name,
      op: entry.entryType,
      attributes: attributes$1
    });
  }
}
function isReact19MeasureEntry(entry) {
  if (entry.entryType !== "measure") {
    return;
  }
  try {
    return entry.detail.devtools.track === "Components \u269B";
  } catch {
    return;
  }
}
function addDetailToSpanAttributes(attributes, entry) {
  try {
    const detail = entry.detail;
    if (!detail) {
      return;
    }
    if (typeof detail === "object") {
      for (const [key, value] of Object.entries(detail)) {
        if (value && core.isPrimitive(value)) {
          attributes[`sentry.browser.measure.detail.${key}`] = value;
        } else if (value !== void 0) {
          try {
            attributes[`sentry.browser.measure.detail.${key}`] = JSON.stringify(value);
          } catch {
          }
        }
      }
      return;
    }
    if (core.isPrimitive(detail)) {
      attributes["sentry.browser.measure.detail"] = detail;
      return;
    }
    try {
      attributes["sentry.browser.measure.detail"] = JSON.stringify(detail);
    } catch {
    }
  } catch {
  }
}

exports._addUserTimingSpan = _addUserTimingSpan;
exports.userTimingIntegration = userTimingIntegration;
//# sourceMappingURL=userTiming.js.map
