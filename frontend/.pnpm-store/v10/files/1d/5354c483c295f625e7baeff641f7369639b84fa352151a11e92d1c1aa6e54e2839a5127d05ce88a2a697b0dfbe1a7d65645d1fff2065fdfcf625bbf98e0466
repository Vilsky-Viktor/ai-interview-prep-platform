import { SENTRY_OP, SENTRY_ORIGIN } from '@sentry/conventions/attributes';
import { defineIntegration, browserPerformanceTimeOrigin, spanToJSON, stringMatchesSomePattern, isPrimitive } from '@sentry/core';
import { getBrowserPerformanceAPI, msToSec, startAndEndSpan } from './utils.js';
import { getNavigationEntry } from '../web-vitals/utils.js';

const INTEGRATION_NAME = "UserTiming";
const _userTimingIntegration = ((options = {}) => {
  return {
    name: INTEGRATION_NAME,
    setup(client) {
      const performance = getBrowserPerformanceAPI();
      const timeOrigin = browserPerformanceTimeOrigin();
      if (!performance?.getEntries || !timeOrigin) {
        return;
      }
      const timeOriginInSeconds = msToSec(timeOrigin);
      let performanceCursor = 0;
      client.on("beforeIdleSpanEnd", (idleSpan) => {
        const { attributes, start_timestamp: parentStartTimestamp } = spanToJSON(idleSpan);
        const parentOp = attributes[SENTRY_OP];
        if (parentOp !== "pageload" && parentOp !== "navigation") {
          return;
        }
        const requestTime = msToSec(getNavigationEntry(false)?.requestStart ?? 0);
        const performanceEntries = performance.getEntries();
        for (const entry of performanceEntries.slice(performanceCursor)) {
          if (entry.entryType !== "mark" && entry.entryType !== "measure") {
            continue;
          }
          const startTime = msToSec(entry.startTime);
          const absoluteStartTime = timeOriginInSeconds + startTime;
          if (parentOp === "navigation" && parentStartTimestamp && absoluteStartTime < parentStartTimestamp) {
            continue;
          }
          _addUserTimingSpan(
            idleSpan,
            entry,
            startTime,
            msToSec(Math.max(0, entry.duration)),
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
const userTimingIntegration = defineIntegration(_userTimingIntegration);
function _addUserTimingSpan(parentSpan, entry, startTime, duration, timeOrigin, requestTime, ignore) {
  if (isReact19MeasureEntry(entry) || stringMatchesSomePattern(entry.name, ignore)) {
    return;
  }
  const spanStartTimestamp = timeOrigin + Math.max(startTime, requestTime);
  const originalStartTimestamp = timeOrigin + startTime;
  const spanEndTimestamp = originalStartTimestamp + duration;
  const attributes = {
    [SENTRY_ORIGIN]: `auto.browser.user_timing.${entry.entryType}`
  };
  if (spanStartTimestamp !== originalStartTimestamp) {
    attributes["sentry.browser.measure_happened_before_request"] = true;
    attributes["sentry.browser.measure_start_time"] = spanStartTimestamp;
  }
  addDetailToSpanAttributes(attributes, entry);
  if (spanStartTimestamp <= spanEndTimestamp) {
    startAndEndSpan(parentSpan, spanStartTimestamp, spanEndTimestamp, {
      name: entry.name,
      op: entry.entryType,
      attributes
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
        if (value && isPrimitive(value)) {
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
    if (isPrimitive(detail)) {
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

export { _addUserTimingSpan, userTimingIntegration };
//# sourceMappingURL=userTiming.js.map
