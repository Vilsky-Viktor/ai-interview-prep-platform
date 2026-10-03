Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const htmlTreeAsString = require('../htmlTreeAsString.js');
const types = require('../types.js');
const performanceObserver = require('../instrumentation/performanceObserver.js');

const LAST_INTERACTIONS = [];
const INTERACTIONS_SPAN_MAP = /* @__PURE__ */ new Map();
const UNKNOWN_ELEMENT_NAME = "<unknown>";
const ELEMENT_NAME_TIMESTAMP_MAP = /* @__PURE__ */ new Map();
const MAX_PLAUSIBLE_INP_DURATION = 60;
const INP_ENTRY_MAP = {
  click: "click",
  pointerdown: "click",
  pointerup: "click",
  mousedown: "click",
  mouseup: "click",
  touchstart: "click",
  touchend: "click",
  mouseover: "hover",
  mouseout: "hover",
  mouseenter: "hover",
  mouseleave: "hover",
  pointerover: "hover",
  pointerout: "hover",
  pointerenter: "hover",
  pointerleave: "hover",
  dragstart: "drag",
  dragend: "drag",
  drag: "drag",
  dragenter: "drag",
  dragleave: "drag",
  dragover: "drag",
  drop: "drag",
  keydown: "press",
  keyup: "press",
  keypress: "press",
  input: "press"
};
function getCachedInteractionContext(interactionId) {
  return interactionId != null ? INTERACTIONS_SPAN_MAP.get(interactionId) : void 0;
}
function registerInpInteractionListener() {
  const interactionEvents = Object.keys(INP_ENTRY_MAP);
  if (core.isBrowser()) {
    interactionEvents.forEach((eventType) => {
      types.WINDOW.addEventListener(eventType, captureElementFromEvent, { capture: true, passive: true });
    });
  }
  function captureElementFromEvent(event) {
    const target = event.target;
    if (!target) {
      return;
    }
    const elementName = htmlTreeAsString.htmlTreeAsString(target);
    const timestamp = Math.round(event.timeStamp);
    if (!elementName || elementName === UNKNOWN_ELEMENT_NAME) {
      return;
    }
    if (ELEMENT_NAME_TIMESTAMP_MAP.has(timestamp)) {
      return;
    }
    ELEMENT_NAME_TIMESTAMP_MAP.set(timestamp, elementName);
    if (ELEMENT_NAME_TIMESTAMP_MAP.size > 50) {
      const firstKey = ELEMENT_NAME_TIMESTAMP_MAP.keys().next().value;
      if (firstKey !== void 0) {
        ELEMENT_NAME_TIMESTAMP_MAP.delete(firstKey);
      }
    }
  }
  function resolveElementNameFromEntry(entry) {
    const timestamp = Math.round(entry.startTime);
    let elementName = ELEMENT_NAME_TIMESTAMP_MAP.get(timestamp);
    if (!elementName) {
      for (let offset = -5; offset <= 5; offset++) {
        const nearbyName = ELEMENT_NAME_TIMESTAMP_MAP.get(timestamp + offset);
        if (nearbyName) {
          elementName = nearbyName;
          break;
        }
      }
    }
    return elementName || UNKNOWN_ELEMENT_NAME;
  }
  const handleEntries = ({ entries }) => {
    const activeSpan = core.getActiveSpan();
    const activeRootSpan = activeSpan && core.getRootSpan(activeSpan);
    entries.forEach((entry) => {
      if (!performanceObserver.isPerformanceEventTiming(entry)) {
        return;
      }
      const interactionId = entry.interactionId;
      if (interactionId == null) {
        return;
      }
      if (INTERACTIONS_SPAN_MAP.has(interactionId)) {
        return;
      }
      const elementName = entry.target ? htmlTreeAsString.htmlTreeAsString(entry.target) : resolveElementNameFromEntry(entry);
      if (LAST_INTERACTIONS.length > 10) {
        const last = LAST_INTERACTIONS.shift();
        INTERACTIONS_SPAN_MAP.delete(last);
      }
      LAST_INTERACTIONS.push(interactionId);
      INTERACTIONS_SPAN_MAP.set(interactionId, {
        span: activeRootSpan,
        elementName
      });
    });
  };
  performanceObserver.addPerformanceInstrumentationHandler("event", handleEntries);
  performanceObserver.addPerformanceInstrumentationHandler("first-input", handleEntries);
}

exports.INP_ENTRY_MAP = INP_ENTRY_MAP;
exports.MAX_PLAUSIBLE_INP_DURATION = MAX_PLAUSIBLE_INP_DURATION;
exports.UNKNOWN_ELEMENT_NAME = UNKNOWN_ELEMENT_NAME;
exports.getCachedInteractionContext = getCachedInteractionContext;
exports.registerInpInteractionListener = registerInpInteractionListener;
//# sourceMappingURL=inp.js.map
