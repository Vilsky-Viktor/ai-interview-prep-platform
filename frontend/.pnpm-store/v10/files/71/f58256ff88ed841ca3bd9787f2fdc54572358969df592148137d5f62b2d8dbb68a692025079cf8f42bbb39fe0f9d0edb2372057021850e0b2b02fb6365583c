Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const attributes = require('@sentry/conventions/attributes');
const debugBuild = require('../debug-build.js');
const htmlTreeAsString = require('../htmlTreeAsString.js');
const performanceObserver = require('../instrumentation/performanceObserver.js');
const utils = require('../performance/utils.js');
const lcp = require('./lcp.js');
const utils$1 = require('./utils.js');

let _measurements = {};
let _lcpEntry;
let _clsEntry;
let _navigationType;
function startTrackingWebVitals({ trackCls, trackLcp }) {
  const performance = utils.getBrowserPerformanceAPI();
  if (performance && core.browserPerformanceTimeOrigin()) {
    const lcpCleanupCallback = trackLcp ? _trackLCP() : void 0;
    const clsCleanupCallback = trackCls ? _trackCLS() : void 0;
    const ttfbCleanupCallback = _trackTtfb();
    const fcpCleanupCallback = _trackFcp();
    const fpCleanupCallback = _trackFp();
    return () => {
      ttfbCleanupCallback();
      fcpCleanupCallback();
      fpCleanupCallback();
      lcpCleanupCallback?.();
      clsCleanupCallback?.();
    };
  }
  return () => void 0;
}
function _trackCLS() {
  return performanceObserver.addClsInstrumentationHandler(({ metric }) => {
    const entry = metric.entries[metric.entries.length - 1];
    if (!entry) {
      return;
    }
    _measurements["cls"] = { value: metric.value, unit: "" };
    _clsEntry = entry;
  }, true);
}
function _trackLCP() {
  return performanceObserver.addLcpInstrumentationHandler(({ metric }) => {
    const entry = metric.entries[metric.entries.length - 1];
    if (!entry || !lcp.isValidLcpMetric(metric.value)) {
      return;
    }
    _measurements["lcp"] = { value: metric.value, unit: "millisecond" };
    _lcpEntry = entry;
  }, true);
}
function _trackTtfb() {
  return performanceObserver.addTtfbInstrumentationHandler(({ metric }) => {
    _navigationType = metric.navigationType;
    const entry = metric.entries[metric.entries.length - 1];
    if (!entry) {
      return;
    }
    _measurements["ttfb"] = { value: metric.value, unit: "millisecond" };
  });
}
function _trackFcp() {
  return performanceObserver.addFcpInstrumentationHandler(({ metric }) => {
    _navigationType = metric.navigationType;
    _measurements["fcp"] = { value: metric.value, unit: "millisecond" };
  });
}
function _trackFp() {
  return performanceObserver.addPerformanceInstrumentationHandler("paint", ({ entries }) => {
    const firstHidden = utils$1.getVisibilityWatcher();
    for (const entry of entries) {
      if (entry.name === "first-paint" && entry.startTime < firstHidden.firstHiddenTime) {
        _measurements["fp"] = { value: entry.startTime, unit: "millisecond" };
      }
    }
  });
}
function addWebVitalsToSpan(span, options) {
  const origin = core.browserPerformanceTimeOrigin();
  if (!utils.getBrowserPerformanceAPI()?.getEntries || !origin) {
    resetWebVitalState();
    return;
  }
  const { spanStreamingEnabled, recordClsOnPageloadSpan, recordLcpOnPageloadSpan } = options;
  const timeOrigin = utils.msToSec(origin);
  if (core.spanToJSON(span).attributes[attributes.SENTRY_OP] === "pageload") {
    _addTtfbRequestTimeToMeasurements(_measurements);
    _rebaseFpAgainstActivationStart(_measurements);
    if (spanStreamingEnabled) {
      const setAttr = (shortWebVitalName, value, customAttrName) => {
        const attrKey = customAttrName ?? `browser.web_vital.${shortWebVitalName}.value`;
        span.setAttribute(attrKey, value);
        debugBuild.DEBUG_BUILD && core.debug.log("Setting web vital attribute", { [attrKey]: value }, "on pageload span");
      };
      ["ttfb", "fp", "fcp"].forEach((measurementName) => {
        if (_measurements[measurementName]) {
          setAttr(measurementName, _measurements[measurementName].value);
        }
      });
      if (_measurements["ttfb.requestTime"]) {
        setAttr("ttfb.requestTime", _measurements["ttfb.requestTime"].value, "browser.web_vital.ttfb.request_time");
      }
    } else {
      if (!recordClsOnPageloadSpan) {
        delete _measurements.cls;
      }
      if (!recordLcpOnPageloadSpan) {
        delete _measurements.lcp;
      }
      Object.entries(_measurements).forEach(([measurementName, measurement]) => {
        core.setMeasurement(measurementName, measurement.value, measurement.unit, span);
      });
      _setWebVitalAttributes(span, options);
    }
    if (_navigationType) {
      span.setAttribute(attributes.BROWSER_NAVIGATION_TYPE, _navigationType);
    }
    span.setAttribute(spanStreamingEnabled ? "browser.performance.time_origin" : "performance.timeOrigin", timeOrigin);
    span.setAttribute(
      spanStreamingEnabled ? "browser.performance.navigation.activation_start" : "performance.activationStart",
      utils$1.getActivationStart()
    );
  }
  resetWebVitalState();
}
function resetWebVitalState() {
  _lcpEntry = void 0;
  _clsEntry = void 0;
  _navigationType = void 0;
  _measurements = {};
}
function _setWebVitalAttributes(span, options) {
  if (_lcpEntry && options.recordLcpOnPageloadSpan) {
    if (_lcpEntry.element) {
      span.setAttribute("lcp.element", htmlTreeAsString.htmlTreeAsString(_lcpEntry.element));
    }
    if (_lcpEntry.id) {
      span.setAttribute("lcp.id", _lcpEntry.id);
    }
    if (_lcpEntry.url) {
      span.setAttribute("lcp.url", _lcpEntry.url.trim().slice(0, 200));
    }
    if (_lcpEntry.loadTime != null) {
      span.setAttribute("lcp.loadTime", _lcpEntry.loadTime);
    }
    if (_lcpEntry.renderTime != null) {
      span.setAttribute("lcp.renderTime", _lcpEntry.renderTime);
    }
    span.setAttribute("lcp.size", _lcpEntry.size);
  }
  if (_clsEntry?.sources && options.recordClsOnPageloadSpan) {
    _clsEntry.sources.forEach(
      (source, index) => span.setAttribute(`cls.source.${index + 1}`, htmlTreeAsString.htmlTreeAsString(source.node))
    );
  }
}
function _rebaseFpAgainstActivationStart(measurements) {
  const fp = measurements["fp"];
  if (fp) {
    fp.value = Math.max(fp.value - utils$1.getActivationStart(), 0);
  }
}
function _addTtfbRequestTimeToMeasurements(_measurements2) {
  const navEntry = utils$1.getNavigationEntry(false);
  if (!navEntry) {
    return;
  }
  const { responseStart, requestStart } = navEntry;
  if (requestStart <= responseStart) {
    _measurements2["ttfb.requestTime"] = {
      value: responseStart - requestStart,
      unit: "millisecond"
    };
  }
}

exports.addWebVitalsToSpan = addWebVitalsToSpan;
exports.startTrackingWebVitals = startTrackingWebVitals;
//# sourceMappingURL=tracking.js.map
