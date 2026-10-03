import { addHandler, maybeInstrument, triggerHandlers, fill, addNonEnumerableProperty, uuid4 } from '@sentry/core';
import { WINDOW } from '../types.js';

const DEBOUNCE_DURATION = 1e3;
let debounceTimerID;
let lastCapturedEventType;
let lastCapturedEventTargetId;
function getCapture(options) {
  return typeof options === "boolean" ? options : !!options?.capture;
}
function addClickKeypressInstrumentationHandler(handler) {
  const type = "dom";
  addHandler(type, handler);
  maybeInstrument(type, instrumentDOM);
}
function instrumentDOM() {
  if (!WINDOW.document) {
    return;
  }
  const triggerDOMHandler = triggerHandlers.bind(null, "dom");
  const globalDOMEventHandler = makeDOMEventHandler(triggerDOMHandler, true);
  WINDOW.document.addEventListener("click", globalDOMEventHandler, false);
  WINDOW.document.addEventListener("keypress", globalDOMEventHandler, false);
  ["EventTarget", "Node"].forEach((target) => {
    const globalObject = WINDOW;
    const proto = globalObject[target]?.prototype;
    if (!proto?.hasOwnProperty?.("addEventListener")) {
      return;
    }
    fill(proto, "addEventListener", function(originalAddEventListener) {
      return function(type, listener, options) {
        if ((type === "click" || type == "keypress") && listener) {
          try {
            const handlers = this.__sentry_instrumentation_handlers__ = this.__sentry_instrumentation_handlers__ || {};
            const handlerForType = handlers[type] = handlers[type] || {
              captureListeners: /* @__PURE__ */ new WeakSet(),
              bubbleListeners: /* @__PURE__ */ new WeakSet(),
              listenerCount: 0
            };
            const capture = getCapture(options);
            if (!handlerForType.handler) {
              const handler = makeDOMEventHandler(triggerDOMHandler);
              handlerForType.handler = handler;
              handlerForType.capture = capture;
              originalAddEventListener.call(this, type, handler, handlerForType.capture);
            }
            const listeners = handlerForType[capture ? "captureListeners" : "bubbleListeners"];
            if (!listeners.has(listener)) {
              if (typeof options === "object" && (options?.once || options?.signal)) {
                handlerForType.sticky = true;
              } else {
                listeners.add(listener);
                handlerForType.listenerCount++;
              }
            }
          } catch {
          }
        }
        return originalAddEventListener.call(this, type, listener, options);
      };
    });
    fill(
      proto,
      "removeEventListener",
      function(originalRemoveEventListener) {
        return function(type, listener, options) {
          if ((type === "click" || type == "keypress") && listener) {
            try {
              const handlers = this.__sentry_instrumentation_handlers__ || {};
              const handlerForType = handlers[type];
              if (handlerForType?.[getCapture(options) ? "captureListeners" : "bubbleListeners"].delete(listener)) {
                if (!--handlerForType.listenerCount && !handlerForType.sticky) {
                  originalRemoveEventListener.call(this, type, handlerForType.handler, handlerForType.capture);
                  handlerForType.handler = void 0;
                  delete handlers[type];
                }
                if (Object.keys(handlers).length === 0) {
                  delete this.__sentry_instrumentation_handlers__;
                }
              }
            } catch {
            }
          }
          return originalRemoveEventListener.call(this, type, listener, options);
        };
      }
    );
  });
}
function isSimilarToLastCapturedEvent(event) {
  if (event.type !== lastCapturedEventType) {
    return false;
  }
  try {
    if (!event.target || event.target._sentryId !== lastCapturedEventTargetId) {
      return false;
    }
  } catch {
  }
  return true;
}
function shouldSkipDOMEvent(eventType, target) {
  if (eventType !== "keypress") {
    return false;
  }
  if (!target?.tagName) {
    return true;
  }
  if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
    return false;
  }
  return true;
}
function makeDOMEventHandler(handler, globalListener = false) {
  return (event) => {
    if (!event || event["_sentryCaptured"]) {
      return;
    }
    const target = getEventTarget(event);
    if (shouldSkipDOMEvent(event.type, target)) {
      return;
    }
    addNonEnumerableProperty(event, "_sentryCaptured", true);
    if (target && !target._sentryId) {
      addNonEnumerableProperty(target, "_sentryId", uuid4());
    }
    const name = event.type === "keypress" ? "input" : event.type;
    if (!isSimilarToLastCapturedEvent(event)) {
      const handlerData = { event, name, global: globalListener };
      handler(handlerData);
      lastCapturedEventType = event.type;
      lastCapturedEventTargetId = target ? target._sentryId : void 0;
    }
    clearTimeout(debounceTimerID);
    debounceTimerID = WINDOW.setTimeout(() => {
      lastCapturedEventTargetId = void 0;
      lastCapturedEventType = void 0;
    }, DEBOUNCE_DURATION);
  };
}
function getEventTarget(event) {
  try {
    return event.target;
  } catch {
    return null;
  }
}

export { addClickKeypressInstrumentationHandler, instrumentDOM };
//# sourceMappingURL=dom.js.map
