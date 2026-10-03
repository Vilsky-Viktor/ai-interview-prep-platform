import { browserPerformanceTimeOrigin, spanToJSON, getActiveSpan, UI_LONG_TASK_SPAN_NAME_FALLBACK, parseUrl, filterCollectedUrl, RESOURCE_SPAN_NAME_FALLBACK, SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN, setMeasurement, BROWSER_NAVIGATION_TIMING_SPAN_NAMES } from '@sentry/core';
import { SENTRY_OP, CODE_FILE_PATH, CODE_FUNCTION_NAME, BROWSER_PAINT_TYPE, NETWORK_CONNECTION_EFFECTIVE_TYPE, NETWORK_CONNECTION_TYPE, NETWORK_CONNECTION_RTT, URL_FULL, URL_SCHEME, SERVER_ADDRESS, URL_DOMAIN, HTTP_REQUEST_SAME_ORIGIN, HTTP_RESPONSE_STATUS_CODE, HTTP_RESPONSE_SIZE, HTTP_RESPONSE_BODY_SIZE } from '@sentry/conventions/attributes';
import { UI_LONG_ANIMATION_FRAME, RESOURCE_OTHER, BROWSER_PAINT, BROWSER_LOAD_EVENT, BROWSER_DOM_CONTENT_LOADED_EVENT, BROWSER_CONNECT, BROWSER_REDIRECT, BROWSER_UNLOAD_EVENT, BROWSER_DNS, BROWSER_CACHE, BROWSER_TLS_SSL, BROWSER_REQUEST, BROWSER_RESPONSE, UI_LONG_TASK } from '@sentry/conventions/op';
import { addPerformanceInstrumentationHandler } from '../instrumentation/performanceObserver.js';
import { WINDOW } from '../types.js';
import { resourceTimingToSpanAttributes } from './resourceTiming.js';
import { getBrowserPerformanceAPI, msToSec, startAndEndSpan, isMeasurementValue } from './utils.js';

const MAX_INT_AS_BYTES = 2147483647;
let _performanceCursor = 0;
function startTrackingLongTasks() {
  addPerformanceInstrumentationHandler("longtask", ({ entries }) => {
    const parent = getActiveSpan();
    if (!parent) {
      return;
    }
    const { attributes: parentAttributes, start_timestamp: parentStartTimestamp } = spanToJSON(parent);
    for (const entry of entries) {
      const startTime = msToSec(browserPerformanceTimeOrigin() + entry.startTime);
      const duration = msToSec(entry.duration);
      if (parentAttributes[SENTRY_OP] === "navigation" && parentStartTimestamp && startTime < parentStartTimestamp) {
        continue;
      }
      startAndEndSpan(parent, startTime, startTime + duration, {
        name: UI_LONG_TASK_SPAN_NAME_FALLBACK,
        op: UI_LONG_TASK,
        attributes: {
          [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.browser.metrics"
        }
      });
    }
  });
}
function startTrackingLongAnimationFrames() {
  const observer = new PerformanceObserver((list) => {
    const parent = getActiveSpan();
    if (!parent) {
      return;
    }
    for (const entry of list.getEntries()) {
      if (!entry.scripts[0]) {
        continue;
      }
      const startTime = msToSec(browserPerformanceTimeOrigin() + entry.startTime);
      const {
        start_timestamp: parentStartTimestamp,
        attributes: { [SENTRY_OP]: parentOp }
      } = spanToJSON(parent);
      if (parentOp === "navigation" && parentStartTimestamp && startTime < parentStartTimestamp) {
        continue;
      }
      const duration = msToSec(entry.duration);
      const attributes = {
        [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.browser.metrics"
      };
      const initialScript = entry.scripts[0];
      const { invoker, invokerType, sourceURL, sourceFunctionName, sourceCharPosition } = initialScript;
      attributes["browser.script.invoker"] = invoker;
      attributes["browser.script.invoker_type"] = invokerType;
      if (sourceURL) {
        attributes[CODE_FILE_PATH] = sourceURL;
      }
      if (sourceFunctionName) {
        attributes[CODE_FUNCTION_NAME] = sourceFunctionName;
      }
      if (sourceCharPosition !== -1) {
        attributes["browser.script.source_char_position"] = sourceCharPosition;
      }
      startAndEndSpan(parent, startTime, startTime + duration, {
        name: UI_LONG_TASK_SPAN_NAME_FALLBACK,
        op: UI_LONG_ANIMATION_FRAME,
        attributes
      });
    }
  });
  observer.observe({ type: "long-animation-frame", buffered: true });
}
function addPerformanceEntries(span, options) {
  const performance = getBrowserPerformanceAPI();
  const origin = browserPerformanceTimeOrigin();
  if (!performance?.getEntries || !origin) {
    return;
  }
  const { spanStreamingEnabled, ignoreResourceSpans } = options;
  const timeOrigin = msToSec(origin);
  const performanceEntries = performance.getEntries();
  const { attributes, start_timestamp: transactionStartTime } = spanToJSON(span);
  performanceEntries.slice(_performanceCursor).forEach((entry) => {
    const startTime = msToSec(entry.startTime);
    const duration = msToSec(
      // Inexplicably, Chrome sometimes emits a negative duration. We need to work around this.
      // There is a SO post attempting to explain this, but it leaves one with open questions: https://stackoverflow.com/questions/23191918/peformance-getentries-and-negative-duration-display
      // The way we clamp the value is probably not accurate, since we have observed this happen for things that may take a while to load, like for example the replay worker.
      // TODO: Investigate why this happens and how to properly mitigate. For now, this is a workaround to prevent transactions being dropped due to negative duration spans.
      Math.max(0, entry.duration)
    );
    if (attributes[SENTRY_OP] === "navigation" && transactionStartTime && timeOrigin + startTime < transactionStartTime) {
      return;
    }
    switch (entry.entryType) {
      case "navigation": {
        _addNavigationSpans(span, entry, timeOrigin, spanStreamingEnabled);
        break;
      }
      case "paint": {
        _addPaintSpan(span, entry, startTime, duration, timeOrigin);
        break;
      }
      case "resource": {
        _addResourceSpans(
          span,
          entry,
          entry.name,
          startTime,
          duration,
          timeOrigin,
          ignoreResourceSpans,
          spanStreamingEnabled
        );
        break;
      }
    }
  });
  _performanceCursor = Math.max(performanceEntries.length - 1, 0);
  _trackNavigator(span, spanStreamingEnabled);
}
function _addPaintSpan(span, entry, startTime, duration, timeOrigin) {
  const startTimestamp = timeOrigin + startTime;
  startAndEndSpan(span, startTimestamp, startTimestamp + duration, {
    // The entry name (`first-paint`, `first-contentful-paint`) is already the low-cardinality name
    // the conventions ask for, so only the attribute backing it has to be added.
    name: entry.name,
    attributes: {
      [SENTRY_OP]: BROWSER_PAINT,
      [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.resource.browser.metrics",
      [BROWSER_PAINT_TYPE]: entry.name
    }
  });
}
function _addNavigationSpans(span, entry, timeOrigin, spanStreamingEnabled) {
  _addPerformanceNavigationTiming(span, entry, "unloadEvent", timeOrigin, spanStreamingEnabled);
  _addPerformanceNavigationTiming(span, entry, "redirect", timeOrigin, spanStreamingEnabled);
  _addPerformanceNavigationTiming(span, entry, "domContentLoadedEvent", timeOrigin, spanStreamingEnabled);
  _addPerformanceNavigationTiming(span, entry, "loadEvent", timeOrigin, spanStreamingEnabled);
  _addPerformanceNavigationTiming(span, entry, "connect", timeOrigin, spanStreamingEnabled);
  _addPerformanceNavigationTiming(span, entry, "secureConnection", timeOrigin, spanStreamingEnabled);
  _addPerformanceNavigationTiming(span, entry, "fetch", timeOrigin, spanStreamingEnabled);
  _addPerformanceNavigationTiming(span, entry, "domainLookup", timeOrigin, spanStreamingEnabled);
  _addRequest(span, entry, timeOrigin, spanStreamingEnabled);
}
const NAVIGATION_TIMING_SPAN_OPS = {
  secureConnection: BROWSER_TLS_SSL,
  fetch: BROWSER_CACHE,
  domainLookup: BROWSER_DNS,
  unloadEvent: BROWSER_UNLOAD_EVENT,
  redirect: BROWSER_REDIRECT,
  connect: BROWSER_CONNECT,
  domContentLoadedEvent: BROWSER_DOM_CONTENT_LOADED_EVENT,
  loadEvent: BROWSER_LOAD_EVENT
};
function _addPerformanceNavigationTiming(span, entry, event, timeOrigin, spanStreamingEnabled) {
  const eventEnd = _getEndPropertyNameForNavigationTiming(event);
  const end = entry[eventEnd];
  const start = entry[`${event}Start`];
  if (!start || !end) {
    return;
  }
  const op = NAVIGATION_TIMING_SPAN_OPS[event];
  startAndEndSpan(span, timeOrigin + msToSec(start), timeOrigin + msToSec(end), {
    // With span streaming, span names have to be low cardinality, so we can't fall back to the
    // document URL. `url.full` keeps it, and is what Relay derives the description from.
    name: spanStreamingEnabled ? BROWSER_NAVIGATION_TIMING_SPAN_NAMES[op] : entry.name,
    attributes: {
      [SENTRY_OP]: op,
      [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.browser.metrics",
      [URL_FULL]: filterCollectedUrl(entry.name),
      ...event === "redirect" && entry.redirectCount != null ? { "http.redirect_count": entry.redirectCount } : {}
    }
  });
}
function _getEndPropertyNameForNavigationTiming(event) {
  if (event === "secureConnection") {
    return "connectEnd";
  }
  if (event === "fetch") {
    return "domainLookupStart";
  }
  return `${event}End`;
}
function _addRequest(span, entry, timeOrigin, spanStreamingEnabled) {
  const requestStartTimestamp = timeOrigin + msToSec(entry.requestStart);
  const responseEndTimestamp = timeOrigin + msToSec(entry.responseEnd);
  const responseStartTimestamp = timeOrigin + msToSec(entry.responseStart);
  if (entry.responseEnd) {
    const url = filterCollectedUrl(entry.name);
    startAndEndSpan(span, requestStartTimestamp, responseEndTimestamp, {
      name: spanStreamingEnabled ? BROWSER_NAVIGATION_TIMING_SPAN_NAMES[BROWSER_REQUEST] : entry.name,
      attributes: {
        [SENTRY_OP]: BROWSER_REQUEST,
        [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.browser.metrics",
        [URL_FULL]: url
      }
    });
    startAndEndSpan(span, responseStartTimestamp, responseEndTimestamp, {
      name: spanStreamingEnabled ? BROWSER_NAVIGATION_TIMING_SPAN_NAMES[BROWSER_RESPONSE] : entry.name,
      attributes: {
        [SENTRY_OP]: BROWSER_RESPONSE,
        [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.browser.metrics",
        [URL_FULL]: url
      }
    });
  }
}
function _addResourceSpans(span, entry, resourceUrl, startTime, duration, timeOrigin, ignoredResourceSpanOps, spanStreamingEnabled) {
  if (entry.initiatorType === "xmlhttprequest" || entry.initiatorType === "fetch") {
    return;
  }
  const op = entry.initiatorType ? `resource.${entry.initiatorType}` : RESOURCE_OTHER;
  if (ignoredResourceSpanOps?.includes(op)) {
    return;
  }
  const attributes = {
    [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.resource.browser.metrics"
  };
  const parsedUrl = parseUrl(resourceUrl);
  if (parsedUrl.protocol) {
    attributes[URL_SCHEME] = parsedUrl.protocol.split(":").pop();
  }
  const host = parsedUrl.host?.replace(/^.*@/, "");
  if (host) {
    attributes[SERVER_ADDRESS] = host;
  }
  const domain = host?.replace(/:\d+$/, "");
  if (domain) {
    attributes[URL_DOMAIN] = domain;
  }
  attributes[HTTP_REQUEST_SAME_ORIGIN] = resourceUrl.includes(WINDOW.location.origin);
  attributes[URL_FULL] = filterCollectedUrl(resourceUrl);
  _setResourceRequestAttributes(entry, attributes, [
    // https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming/responseStatus
    ["responseStatus", HTTP_RESPONSE_STATUS_CODE],
    ["transferSize", HTTP_RESPONSE_SIZE],
    ["encodedBodySize", HTTP_RESPONSE_BODY_SIZE],
    ["decodedBodySize", "http.response.body.decoded_size"],
    // https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming/renderBlockingStatus
    ["renderBlockingStatus", "resource.render_blocking_status"],
    // https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming/deliveryType
    ["deliveryType", "http.response_delivery_type"]
  ]);
  const attributesWithResourceTiming = { ...attributes, ...resourceTimingToSpanAttributes(entry) };
  const startTimestamp = timeOrigin + startTime;
  const endTimestamp = startTimestamp + duration;
  startAndEndSpan(span, startTimestamp, endTimestamp, {
    // With span streaming, span names have to be low cardinality, so we can't fall back to the URL.
    name: spanStreamingEnabled ? domain || RESOURCE_SPAN_NAME_FALLBACK : resourceUrl.replace(WINDOW.location.origin, ""),
    op,
    attributes: attributesWithResourceTiming
  });
}
function _trackNavigator(span, spanStreamingEnabled) {
  const navigator = WINDOW.navigator;
  if (!navigator) {
    return;
  }
  const connection = navigator.connection;
  if (connection) {
    if (connection.effectiveType) {
      span.setAttribute(
        spanStreamingEnabled ? NETWORK_CONNECTION_EFFECTIVE_TYPE : "effectiveConnectionType",
        connection.effectiveType
      );
    }
    if (connection.type) {
      span.setAttribute(spanStreamingEnabled ? NETWORK_CONNECTION_TYPE : "connectionType", connection.type);
    }
    if (isMeasurementValue(connection.rtt)) {
      if (spanStreamingEnabled) {
        span.setAttribute(NETWORK_CONNECTION_RTT, connection.rtt);
      } else if (spanToJSON(span).attributes[SENTRY_OP] === "pageload") {
        setMeasurement("connection.rtt", connection.rtt, "millisecond");
      }
    }
  }
  if (isMeasurementValue(navigator.deviceMemory)) {
    if (spanStreamingEnabled) {
      span.setAttribute("device.memory.estimated_capacity", navigator.deviceMemory);
    } else {
      span.setAttribute("deviceMemory", `${navigator.deviceMemory} GB`);
    }
  }
  if (isMeasurementValue(navigator.hardwareConcurrency)) {
    if (spanStreamingEnabled) {
      span.setAttribute("device.processor_count", navigator.hardwareConcurrency);
    } else {
      span.setAttribute("hardwareConcurrency", String(navigator.hardwareConcurrency));
    }
  }
}
function _setResourceRequestAttributes(entry, attributes, properties) {
  properties.forEach(([entryKey, attributeKey]) => {
    const entryVal = entry[entryKey];
    if (entryVal != null && (typeof entryVal === "number" && entryVal < MAX_INT_AS_BYTES || typeof entryVal === "string")) {
      attributes[attributeKey] = entryVal;
    }
  });
}

export { _addNavigationSpans, _addPaintSpan, _addResourceSpans, _setResourceRequestAttributes, addPerformanceEntries, startTrackingLongAnimationFrames, startTrackingLongTasks };
//# sourceMappingURL=entries.js.map
