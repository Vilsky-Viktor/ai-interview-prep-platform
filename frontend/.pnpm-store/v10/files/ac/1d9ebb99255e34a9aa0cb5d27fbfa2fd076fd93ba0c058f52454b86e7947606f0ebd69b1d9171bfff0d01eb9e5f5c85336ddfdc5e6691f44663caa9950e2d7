Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const debugBuild = require('../debug-build.js');
const htmlTreeAsString = require('../htmlTreeAsString.js');
const componentName = require('../component-name.js');
const inp = require('./inp.js');
const performanceObserver = require('../instrumentation/performanceObserver.js');
const attributes = require('@sentry/conventions/attributes');
const emitSpan = require('./emitSpan.js');
const lcp = require('./lcp.js');
const reportEvents = require('./reportEvents.js');
const softNavs = require('./softNavs.js');
const utils = require('../performance/utils.js');
const op = require('@sentry/conventions/op');

const INTERACTION_TYPE_TO_SPAN_OP = {
  click: op.UI_INTERACTION_CLICK,
  hover: op.UI_INTERACTION_HOVER,
  drag: op.UI_INTERACTION_DRAG,
  press: op.UI_INTERACTION_PRESS
};
const INTERACTION_TYPE_TO_SPAN_NAME_FALLBACK = {
  click: core.UI_INTERACTION_CLICK_SPAN_NAME_FALLBACK,
  hover: core.UI_INTERACTION_HOVER_SPAN_NAME_FALLBACK,
  drag: core.UI_INTERACTION_DRAG_SPAN_NAME_FALLBACK,
  press: core.UI_INTERACTION_PRESS_SPAN_NAME_FALLBACK
};
function trackWebVitalPerNavigation(client, addInstrumentationHandler, send) {
  let pageloadSpan;
  client.on("afterStartPageLoadSpan", (span) => {
    pageloadSpan = span;
  });
  let bfcacheNavigationSpan;
  client.on("spanStart", (span) => {
    const attributes$1 = core.spanToJSON(span).attributes;
    if (attributes$1?.[core.SEMANTIC_ATTRIBUTE_SENTRY_OP] === op.NAVIGATION && attributes$1[attributes.BROWSER_NAVIGATION_TYPE] === "back-forward-cache") {
      bfcacheNavigationSpan = span;
    }
  });
  addInstrumentationHandler(({ metric }) => {
    const navigationSpan = softNavs.getNavigationSpanForMetric(metric);
    if (metric.navigationType === "soft-navigation") {
      if (navigationSpan) {
        send(metric, navigationSpan, metric.navigationId);
      } else {
        debugBuild.DEBUG_BUILD && core.debug.log(`[SoftNav] Dropping ${metric.name} for uncorrelated soft navigation ${metric.navigationId}`);
      }
      return;
    }
    if (metric.navigationType === "back-forward-cache") {
      send(metric, bfcacheNavigationSpan, void 0);
      return;
    }
    send(metric, pageloadSpan, void 0);
  });
}
function trackLcpAsSpan(client, perNavigation = false) {
  if (!utils.supportsWebVital("largest-contentful-paint")) {
    return;
  }
  if (perNavigation) {
    trackWebVitalPerNavigation(client, performanceObserver.addLcpInstrumentationHandler, (metric, parentSpan, softNavigationId) => {
      const entry = metric.entries[metric.entries.length - 1];
      _sendLcpSpan(
        metric.value,
        entry,
        parentSpan,
        softNavigationId,
        metric.navigationType,
        metric.navigationStartTime
      );
    });
    return;
  }
  let lcpValue = 0;
  let lcpEntry;
  let lcpNavigationType;
  const cleanupLcpHandler = performanceObserver.addLcpInstrumentationHandler(({ metric }) => {
    lcpNavigationType = metric.navigationType;
    const entry = metric.entries[metric.entries.length - 1];
    if (!entry || !lcp.isValidLcpMetric(metric.value)) {
      return;
    }
    lcpValue = metric.value;
    lcpEntry = entry;
  }, true);
  reportEvents.listenForWebVitalReportEvents(client, (pageloadSpan) => {
    _sendLcpSpan(lcpValue, lcpEntry, pageloadSpan, void 0, lcpNavigationType);
    cleanupLcpHandler();
  });
}
function _sendLcpSpan(lcpValue, entry, pageloadSpan, softNavigationId, navigationType, navigationStartTime) {
  if (!lcp.isValidLcpMetric(lcpValue)) {
    return;
  }
  debugBuild.DEBUG_BUILD && core.debug.log(`Sending LCP span (${lcpValue})`);
  const performanceTimeOrigin = core.browserPerformanceTimeOrigin() || 0;
  const startTime = utils.msToSec(performanceTimeOrigin + (navigationStartTime || 0));
  const endTime = entry ? utils.msToSec(performanceTimeOrigin + entry.startTime) : startTime + utils.msToSec(lcpValue);
  const selector = entry ? htmlTreeAsString.htmlTreeAsString(entry.element) : void 0;
  const componentName$1 = entry?.element ? componentName.getComponentName(entry.element) : null;
  const client = core.getClient();
  const hasSpanStreaming = !!client && core.hasSpanStreamingEnabled(client);
  const name = hasSpanStreaming ? componentName$1 || core.UI_WEBVITAL_LCP_SPAN_NAME_FALLBACK : selector ?? core.UI_WEBVITAL_LCP_SPAN_NAME_FALLBACK;
  const attributes$1 = {};
  if (selector) {
    attributes$1["browser.web_vital.lcp.element"] = selector;
  }
  if (componentName$1) {
    attributes$1[attributes.UI_COMPONENT_NAME] = componentName$1;
  }
  entry?.id && (attributes$1["browser.web_vital.lcp.id"] = entry.id);
  entry?.url && (attributes$1["browser.web_vital.lcp.url"] = entry.url);
  entry?.loadTime != null && (attributes$1["browser.web_vital.lcp.load_time"] = entry.loadTime);
  entry?.renderTime != null && (attributes$1["browser.web_vital.lcp.render_time"] = entry.renderTime);
  entry?.size != null && (attributes$1["browser.web_vital.lcp.size"] = entry.size);
  emitSpan._emitWebVitalSpan({
    name,
    op: op.UI_WEBVITAL_LCP,
    origin: "auto.http.browser.lcp",
    metricName: "lcp",
    value: lcpValue,
    attributes: attributes$1,
    parentSpan: pageloadSpan,
    startTime,
    endTime,
    softNavigationId,
    navigationType
  });
}
function trackClsAsSpan(client, perNavigation = false) {
  if (!utils.supportsWebVital("layout-shift")) {
    return;
  }
  if (perNavigation) {
    trackWebVitalPerNavigation(client, performanceObserver.addClsInstrumentationHandler, (metric, parentSpan, softNavigationId) => {
      const entry = metric.entries[metric.entries.length - 1];
      _sendClsSpan(
        metric.value,
        entry,
        parentSpan,
        softNavigationId,
        metric.navigationType,
        metric.navigationStartTime
      );
    });
    return;
  }
  let clsValue = 0;
  let clsEntry;
  let clsNavigationType;
  const cleanupClsHandler = performanceObserver.addClsInstrumentationHandler(({ metric }) => {
    clsNavigationType = metric.navigationType;
    const entry = metric.entries[metric.entries.length - 1];
    if (!entry) {
      return;
    }
    clsValue = metric.value;
    clsEntry = entry;
  }, true);
  reportEvents.listenForWebVitalReportEvents(client, (pageloadSpan) => {
    _sendClsSpan(clsValue, clsEntry, pageloadSpan, void 0, clsNavigationType);
    cleanupClsHandler();
  });
}
function _sendClsSpan(clsValue, entry, pageloadSpan, softNavigationId, navigationType, navigationStartTime) {
  debugBuild.DEBUG_BUILD && core.debug.log(`Sending CLS span (${clsValue})`);
  const performanceTimeOrigin = core.browserPerformanceTimeOrigin();
  const offset = entry?.startTime ?? navigationStartTime ?? 0;
  const startTime = performanceTimeOrigin ? utils.msToSec(performanceTimeOrigin + offset) : core.timestampInSeconds();
  const firstSourceNode = entry?.sources[0]?.node;
  const selector = entry ? htmlTreeAsString.htmlTreeAsString(firstSourceNode) : void 0;
  const componentName$1 = firstSourceNode ? componentName.getComponentName(firstSourceNode) : null;
  const client = core.getClient();
  const hasSpanStreaming = !!client && core.hasSpanStreamingEnabled(client);
  const name = hasSpanStreaming ? componentName$1 || core.UI_WEBVITAL_CLS_SPAN_NAME_FALLBACK : selector ?? core.UI_WEBVITAL_CLS_SPAN_NAME_FALLBACK;
  const attributes$1 = {};
  if (componentName$1) {
    attributes$1[attributes.UI_COMPONENT_NAME] = componentName$1;
  }
  if (entry?.sources) {
    entry.sources.forEach((source, index) => {
      attributes$1[`browser.web_vital.cls.source.${index + 1}`] = htmlTreeAsString.htmlTreeAsString(source.node);
    });
  }
  emitSpan._emitWebVitalSpan({
    name,
    op: op.UI_WEBVITAL_CLS,
    origin: "auto.http.browser.cls",
    metricName: "cls",
    value: clsValue,
    attributes: attributes$1,
    parentSpan: pageloadSpan,
    startTime,
    softNavigationId,
    navigationType
  });
}
function trackInpAsSpan(client, perNavigation = false) {
  const performance = utils.getBrowserPerformanceAPI();
  if (!performance || !core.browserPerformanceTimeOrigin()) {
    return;
  }
  const standalone = !core.hasSpanStreamingEnabled(client);
  if (perNavigation) {
    trackWebVitalPerNavigation(client, performanceObserver.addInpInstrumentationHandler, (metric, parentSpan, softNavigationId) => {
      if (isPlausibleInp(metric)) {
        _sendInpSpan(metric.value, findInpEntry(metric), standalone, parentSpan, softNavigationId, metric);
      }
    });
    return;
  }
  const onInp = ({ metric }) => {
    if (isPlausibleInp(metric)) {
      _sendInpSpan(metric.value, findInpEntry(metric), standalone, void 0, void 0, metric);
    }
  };
  performanceObserver.addInpInstrumentationHandler(onInp);
}
function isPlausibleInp(metric) {
  return metric.value != null && utils.msToSec(metric.value) <= inp.MAX_PLAUSIBLE_INP_DURATION;
}
function findInpEntry(metric) {
  return metric.entries.find((e) => e.duration === metric.value && inp.INP_ENTRY_MAP[e.name]);
}
function _sendInpSpan(inpValue, entry, standalone = false, attributedSpan, softNavigationId, metric) {
  debugBuild.DEBUG_BUILD && core.debug.log(`Sending INP span (${inpValue})`);
  const startTime = utils.msToSec(
    core.browserPerformanceTimeOrigin() + (entry?.startTime ?? metric?.navigationStartTime ?? 0)
  );
  const duration = utils.msToSec(inpValue);
  const entryInteractionType = entry && inp.INP_ENTRY_MAP[entry.name];
  const interactionType = entryInteractionType || "click";
  const cachedContext = entry && inp.getCachedInteractionContext(entry.interactionId);
  const activeSpan = core.getActiveSpan();
  const rootSpan = activeSpan ? core.getRootSpan(activeSpan) : void 0;
  const spanToUse = attributedSpan || cachedContext?.span || rootSpan;
  const selector = cachedContext?.elementName || (entry ? htmlTreeAsString.htmlTreeAsString(entry.target) : void 0);
  const componentName$1 = entry?.target ? componentName.getComponentName(entry.target) : null;
  const client = core.getClient();
  const hasSpanStreaming = !!client && core.hasSpanStreamingEnabled(client);
  const fallbackName = INTERACTION_TYPE_TO_SPAN_NAME_FALLBACK[interactionType];
  const name = hasSpanStreaming ? componentName$1 || fallbackName : selector ?? "Interaction to next paint";
  const attributes$1 = {
    [core.SEMANTIC_ATTRIBUTE_EXCLUSIVE_TIME]: entry?.duration ?? inpValue
  };
  selector && selector !== inp.UNKNOWN_ELEMENT_NAME && (attributes$1[attributes.BROWSER_WEB_VITAL_INP_TARGET] = selector);
  entryInteractionType && (attributes$1[attributes.BROWSER_WEB_VITAL_INP_INTERACTION_TYPE] = entryInteractionType);
  if (componentName$1) {
    attributes$1[attributes.UI_COMPONENT_NAME] = componentName$1;
  }
  emitSpan._emitWebVitalSpan({
    name,
    op: INTERACTION_TYPE_TO_SPAN_OP[interactionType],
    origin: "auto.http.browser.inp",
    metricName: "inp",
    value: inpValue,
    attributes: attributes$1,
    startTime,
    endTime: startTime + duration,
    navigationType: metric?.navigationType,
    parentSpan: spanToUse,
    standalone,
    softNavigationId
  });
}

exports._sendClsSpan = _sendClsSpan;
exports._sendInpSpan = _sendInpSpan;
exports._sendLcpSpan = _sendLcpSpan;
exports.trackClsAsSpan = trackClsAsSpan;
exports.trackInpAsSpan = trackInpAsSpan;
exports.trackLcpAsSpan = trackLcpAsSpan;
//# sourceMappingURL=spans.js.map
