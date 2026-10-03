Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const attributes = require('@sentry/conventions/attributes');
const op = require('@sentry/conventions/op');
const performanceObserver = require('../instrumentation/performanceObserver.js');
const types = require('../types.js');
const resourceTiming = require('./resourceTiming.js');
const utils = require('./utils.js');

const MAX_INT_AS_BYTES = 2147483647;
let _performanceCursor = 0;
function startTrackingLongTasks() {
  performanceObserver.addPerformanceInstrumentationHandler("longtask", ({ entries }) => {
    const parent = core.getActiveSpan();
    if (!parent) {
      return;
    }
    const { attributes: parentAttributes, start_timestamp: parentStartTimestamp } = core.spanToJSON(parent);
    for (const entry of entries) {
      const startTime = utils.msToSec(core.browserPerformanceTimeOrigin() + entry.startTime);
      const duration = utils.msToSec(entry.duration);
      if (parentAttributes[attributes.SENTRY_OP] === "navigation" && parentStartTimestamp && startTime < parentStartTimestamp) {
        continue;
      }
      utils.startAndEndSpan(parent, startTime, startTime + duration, {
        name: core.UI_LONG_TASK_SPAN_NAME_FALLBACK,
        op: op.UI_LONG_TASK,
        attributes: {
          [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.browser.metrics"
        }
      });
    }
  });
}
function startTrackingLongAnimationFrames() {
  const observer = new PerformanceObserver((list) => {
    const parent = core.getActiveSpan();
    if (!parent) {
      return;
    }
    for (const entry of list.getEntries()) {
      if (!entry.scripts[0]) {
        continue;
      }
      const startTime = utils.msToSec(core.browserPerformanceTimeOrigin() + entry.startTime);
      const {
        start_timestamp: parentStartTimestamp,
        attributes: { [attributes.SENTRY_OP]: parentOp }
      } = core.spanToJSON(parent);
      if (parentOp === "navigation" && parentStartTimestamp && startTime < parentStartTimestamp) {
        continue;
      }
      const duration = utils.msToSec(entry.duration);
      const attributes$1 = {
        [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.browser.metrics"
      };
      const initialScript = entry.scripts[0];
      const { invoker, invokerType, sourceURL, sourceFunctionName, sourceCharPosition } = initialScript;
      attributes$1["browser.script.invoker"] = invoker;
      attributes$1["browser.script.invoker_type"] = invokerType;
      if (sourceURL) {
        attributes$1[attributes.CODE_FILE_PATH] = sourceURL;
      }
      if (sourceFunctionName) {
        attributes$1[attributes.CODE_FUNCTION_NAME] = sourceFunctionName;
      }
      if (sourceCharPosition !== -1) {
        attributes$1["browser.script.source_char_position"] = sourceCharPosition;
      }
      utils.startAndEndSpan(parent, startTime, startTime + duration, {
        name: core.UI_LONG_TASK_SPAN_NAME_FALLBACK,
        op: op.UI_LONG_ANIMATION_FRAME,
        attributes: attributes$1
      });
    }
  });
  observer.observe({ type: "long-animation-frame", buffered: true });
}
function addPerformanceEntries(span, options) {
  const performance = utils.getBrowserPerformanceAPI();
  const origin = core.browserPerformanceTimeOrigin();
  if (!performance?.getEntries || !origin) {
    return;
  }
  const { spanStreamingEnabled, ignoreResourceSpans } = options;
  const timeOrigin = utils.msToSec(origin);
  const performanceEntries = performance.getEntries();
  const { attributes: attributes$1, start_timestamp: transactionStartTime } = core.spanToJSON(span);
  performanceEntries.slice(_performanceCursor).forEach((entry) => {
    const startTime = utils.msToSec(entry.startTime);
    const duration = utils.msToSec(
      // Inexplicably, Chrome sometimes emits a negative duration. We need to work around this.
      // There is a SO post attempting to explain this, but it leaves one with open questions: https://stackoverflow.com/questions/23191918/peformance-getentries-and-negative-duration-display
      // The way we clamp the value is probably not accurate, since we have observed this happen for things that may take a while to load, like for example the replay worker.
      // TODO: Investigate why this happens and how to properly mitigate. For now, this is a workaround to prevent transactions being dropped due to negative duration spans.
      Math.max(0, entry.duration)
    );
    if (attributes$1[attributes.SENTRY_OP] === "navigation" && transactionStartTime && timeOrigin + startTime < transactionStartTime) {
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
  utils.startAndEndSpan(span, startTimestamp, startTimestamp + duration, {
    // The entry name (`first-paint`, `first-contentful-paint`) is already the low-cardinality name
    // the conventions ask for, so only the attribute backing it has to be added.
    name: entry.name,
    attributes: {
      [attributes.SENTRY_OP]: op.BROWSER_PAINT,
      [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.resource.browser.metrics",
      [attributes.BROWSER_PAINT_TYPE]: entry.name
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
  secureConnection: op.BROWSER_TLS_SSL,
  fetch: op.BROWSER_CACHE,
  domainLookup: op.BROWSER_DNS,
  unloadEvent: op.BROWSER_UNLOAD_EVENT,
  redirect: op.BROWSER_REDIRECT,
  connect: op.BROWSER_CONNECT,
  domContentLoadedEvent: op.BROWSER_DOM_CONTENT_LOADED_EVENT,
  loadEvent: op.BROWSER_LOAD_EVENT
};
function _addPerformanceNavigationTiming(span, entry, event, timeOrigin, spanStreamingEnabled) {
  const eventEnd = _getEndPropertyNameForNavigationTiming(event);
  const end = entry[eventEnd];
  const start = entry[`${event}Start`];
  if (!start || !end) {
    return;
  }
  const op = NAVIGATION_TIMING_SPAN_OPS[event];
  utils.startAndEndSpan(span, timeOrigin + utils.msToSec(start), timeOrigin + utils.msToSec(end), {
    // With span streaming, span names have to be low cardinality, so we can't fall back to the
    // document URL. `url.full` keeps it, and is what Relay derives the description from.
    name: spanStreamingEnabled ? core.BROWSER_NAVIGATION_TIMING_SPAN_NAMES[op] : entry.name,
    attributes: {
      [attributes.SENTRY_OP]: op,
      [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.browser.metrics",
      [attributes.URL_FULL]: core.filterCollectedUrl(entry.name),
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
  const requestStartTimestamp = timeOrigin + utils.msToSec(entry.requestStart);
  const responseEndTimestamp = timeOrigin + utils.msToSec(entry.responseEnd);
  const responseStartTimestamp = timeOrigin + utils.msToSec(entry.responseStart);
  if (entry.responseEnd) {
    const url = core.filterCollectedUrl(entry.name);
    utils.startAndEndSpan(span, requestStartTimestamp, responseEndTimestamp, {
      name: spanStreamingEnabled ? core.BROWSER_NAVIGATION_TIMING_SPAN_NAMES[op.BROWSER_REQUEST] : entry.name,
      attributes: {
        [attributes.SENTRY_OP]: op.BROWSER_REQUEST,
        [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.browser.metrics",
        [attributes.URL_FULL]: url
      }
    });
    utils.startAndEndSpan(span, responseStartTimestamp, responseEndTimestamp, {
      name: spanStreamingEnabled ? core.BROWSER_NAVIGATION_TIMING_SPAN_NAMES[op.BROWSER_RESPONSE] : entry.name,
      attributes: {
        [attributes.SENTRY_OP]: op.BROWSER_RESPONSE,
        [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.browser.metrics",
        [attributes.URL_FULL]: url
      }
    });
  }
}
function _addResourceSpans(span, entry, resourceUrl, startTime, duration, timeOrigin, ignoredResourceSpanOps, spanStreamingEnabled) {
  if (entry.initiatorType === "xmlhttprequest" || entry.initiatorType === "fetch") {
    return;
  }
  const op$1 = entry.initiatorType ? `resource.${entry.initiatorType}` : op.RESOURCE_OTHER;
  if (ignoredResourceSpanOps?.includes(op$1)) {
    return;
  }
  const attributes$1 = {
    [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.resource.browser.metrics"
  };
  const parsedUrl = core.parseUrl(resourceUrl);
  if (parsedUrl.protocol) {
    attributes$1[attributes.URL_SCHEME] = parsedUrl.protocol.split(":").pop();
  }
  const host = parsedUrl.host?.replace(/^.*@/, "");
  if (host) {
    attributes$1[attributes.SERVER_ADDRESS] = host;
  }
  const domain = host?.replace(/:\d+$/, "");
  if (domain) {
    attributes$1[attributes.URL_DOMAIN] = domain;
  }
  attributes$1[attributes.HTTP_REQUEST_SAME_ORIGIN] = resourceUrl.includes(types.WINDOW.location.origin);
  attributes$1[attributes.URL_FULL] = core.filterCollectedUrl(resourceUrl);
  _setResourceRequestAttributes(entry, attributes$1, [
    // https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming/responseStatus
    ["responseStatus", attributes.HTTP_RESPONSE_STATUS_CODE],
    ["transferSize", attributes.HTTP_RESPONSE_SIZE],
    ["encodedBodySize", attributes.HTTP_RESPONSE_BODY_SIZE],
    ["decodedBodySize", "http.response.body.decoded_size"],
    // https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming/renderBlockingStatus
    ["renderBlockingStatus", "resource.render_blocking_status"],
    // https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming/deliveryType
    ["deliveryType", "http.response_delivery_type"]
  ]);
  const attributesWithResourceTiming = { ...attributes$1, ...resourceTiming.resourceTimingToSpanAttributes(entry) };
  const startTimestamp = timeOrigin + startTime;
  const endTimestamp = startTimestamp + duration;
  utils.startAndEndSpan(span, startTimestamp, endTimestamp, {
    // With span streaming, span names have to be low cardinality, so we can't fall back to the URL.
    name: spanStreamingEnabled ? domain || core.RESOURCE_SPAN_NAME_FALLBACK : resourceUrl.replace(types.WINDOW.location.origin, ""),
    op: op$1,
    attributes: attributesWithResourceTiming
  });
}
function _trackNavigator(span, spanStreamingEnabled) {
  const navigator = types.WINDOW.navigator;
  if (!navigator) {
    return;
  }
  const connection = navigator.connection;
  if (connection) {
    if (connection.effectiveType) {
      span.setAttribute(
        spanStreamingEnabled ? attributes.NETWORK_CONNECTION_EFFECTIVE_TYPE : "effectiveConnectionType",
        connection.effectiveType
      );
    }
    if (connection.type) {
      span.setAttribute(spanStreamingEnabled ? attributes.NETWORK_CONNECTION_TYPE : "connectionType", connection.type);
    }
    if (utils.isMeasurementValue(connection.rtt)) {
      if (spanStreamingEnabled) {
        span.setAttribute(attributes.NETWORK_CONNECTION_RTT, connection.rtt);
      } else if (core.spanToJSON(span).attributes[attributes.SENTRY_OP] === "pageload") {
        core.setMeasurement("connection.rtt", connection.rtt, "millisecond");
      }
    }
  }
  if (utils.isMeasurementValue(navigator.deviceMemory)) {
    if (spanStreamingEnabled) {
      span.setAttribute("device.memory.estimated_capacity", navigator.deviceMemory);
    } else {
      span.setAttribute("deviceMemory", `${navigator.deviceMemory} GB`);
    }
  }
  if (utils.isMeasurementValue(navigator.hardwareConcurrency)) {
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

exports._addNavigationSpans = _addNavigationSpans;
exports._addPaintSpan = _addPaintSpan;
exports._addResourceSpans = _addResourceSpans;
exports._setResourceRequestAttributes = _setResourceRequestAttributes;
exports.addPerformanceEntries = addPerformanceEntries;
exports.startTrackingLongAnimationFrames = startTrackingLongAnimationFrames;
exports.startTrackingLongTasks = startTrackingLongTasks;
//# sourceMappingURL=entries.js.map
