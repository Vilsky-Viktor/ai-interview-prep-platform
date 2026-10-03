Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const webVitals = require('web-vitals');
const debugBuild = require('../debug-build.js');

const handlers = {};
const instrumented = {};
let _previousCls;
let _previousLcp;
let _previousTtfb;
let _previousInp;
let _previousFcp;
const stopListeners = {};
let _reportSoftNavs = false;
let _reportBfcache = false;
function enableSoftNavigationReporting() {
  _reportSoftNavs = true;
}
function enableBfcacheReporting() {
  _reportBfcache = true;
}
function addClsInstrumentationHandler(callback, stopOnCallback = false) {
  return addMetricObserver("cls", callback, instrumentCls, _previousCls, stopOnCallback);
}
function addLcpInstrumentationHandler(callback, stopOnCallback = false) {
  return addMetricObserver("lcp", callback, instrumentLcp, _previousLcp, stopOnCallback);
}
function addTtfbInstrumentationHandler(callback) {
  return addMetricObserver("ttfb", callback, instrumentTtfb, _previousTtfb);
}
function addFcpInstrumentationHandler(callback) {
  return addMetricObserver("fcp", callback, instrumentFcp, _previousFcp);
}
function addInpInstrumentationHandler(callback) {
  return addMetricObserver("inp", callback, instrumentInp, _previousInp);
}
function addPerformanceInstrumentationHandler(type, callback) {
  addHandler(type, callback);
  if (!instrumented[type]) {
    instrumentPerformanceObserver(type);
    instrumented[type] = true;
  }
  return getCleanupCallback(type, callback);
}
function triggerHandlers(type, data) {
  const typeHandlers = handlers[type];
  if (!typeHandlers?.length) {
    return;
  }
  for (const handler of typeHandlers) {
    try {
      handler(data);
    } catch (e) {
      debugBuild.DEBUG_BUILD && core.debug.error(
        `Error while triggering instrumentation handler.
Type: ${type}
Name: ${core.getFunctionName(handler)}
Error:`,
        e
      );
    }
  }
}
function unlessBfcacheDisabled(callback) {
  return (metric) => {
    if (!_reportBfcache && metric.navigationType === "back-forward-cache") {
      return;
    }
    callback(metric);
  };
}
function instrumentCls() {
  return webVitals.onCLS(
    unlessBfcacheDisabled((metric) => {
      triggerHandlers("cls", {
        metric
      });
      _previousCls = metric;
    }),
    // We want the callback to be called whenever the CLS value updates.
    // By default, the callback is only called when the tab goes to the background.
    { reportAllChanges: !_reportSoftNavs && !_reportBfcache, reportSoftNavs: _reportSoftNavs }
  );
}
function instrumentLcp() {
  return webVitals.onLCP(
    unlessBfcacheDisabled((metric) => {
      triggerHandlers("lcp", {
        metric
      });
      _previousLcp = metric;
    }),
    // We want the callback to be called whenever the LCP value updates.
    // By default, the callback is only called when the tab goes to the background.
    { reportAllChanges: !_reportSoftNavs && !_reportBfcache, reportSoftNavs: _reportSoftNavs }
  );
}
function instrumentTtfb() {
  return webVitals.onTTFB(
    unlessBfcacheDisabled((metric) => {
      triggerHandlers("ttfb", {
        metric
      });
      _previousTtfb = metric;
    })
  );
}
function instrumentFcp() {
  return webVitals.onFCP(
    unlessBfcacheDisabled((metric) => {
      triggerHandlers("fcp", {
        metric
      });
      _previousFcp = metric;
    })
  );
}
function instrumentInp() {
  return webVitals.onINP(
    unlessBfcacheDisabled((metric) => {
      triggerHandlers("inp", {
        metric
      });
      _previousInp = metric;
    }),
    { reportSoftNavs: _reportSoftNavs }
  );
}
function addMetricObserver(type, callback, instrumentFn, previousValue, stopOnCallback = false) {
  addHandler(type, callback);
  if (!instrumented[type]) {
    instrumented[type] = true;
    void Promise.resolve().then(() => {
      stopListeners[type] = instrumentFn();
    });
  }
  if (previousValue) {
    callback({ metric: previousValue });
  }
  return getCleanupCallback(type, callback, stopOnCallback);
}
function instrumentPerformanceObserver(type) {
  const options = { type, buffered: true };
  if (type === "event") {
    options.durationThreshold = 0;
  }
  try {
    if (PerformanceObserver.supportedEntryTypes.includes(type)) {
      const po = new PerformanceObserver((list) => {
        void Promise.resolve().then(() => {
          triggerHandlers(type, { entries: list.getEntries() });
        });
      });
      po.observe(options);
    }
  } catch {
  }
}
function addHandler(type, handler) {
  handlers[type] = handlers[type] || [];
  handlers[type].push(handler);
}
function getCleanupCallback(type, callback, stopOnCleanup = false) {
  return () => {
    if (stopOnCleanup) {
      stopListeners[type]?.();
    }
    const typeHandlers = handlers[type];
    if (!typeHandlers) {
      return;
    }
    const index = typeHandlers.indexOf(callback);
    if (index !== -1) {
      typeHandlers.splice(index, 1);
    }
  };
}
function isPerformanceEventTiming(entry) {
  return "duration" in entry;
}

exports.addClsInstrumentationHandler = addClsInstrumentationHandler;
exports.addFcpInstrumentationHandler = addFcpInstrumentationHandler;
exports.addInpInstrumentationHandler = addInpInstrumentationHandler;
exports.addLcpInstrumentationHandler = addLcpInstrumentationHandler;
exports.addPerformanceInstrumentationHandler = addPerformanceInstrumentationHandler;
exports.addTtfbInstrumentationHandler = addTtfbInstrumentationHandler;
exports.enableBfcacheReporting = enableBfcacheReporting;
exports.enableSoftNavigationReporting = enableSoftNavigationReporting;
exports.isPerformanceEventTiming = isPerformanceEventTiming;
//# sourceMappingURL=performanceObserver.js.map
