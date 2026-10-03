Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const helpers = require('../helpers.js');

const DEFAULT_EVENT_TARGET = "EventTarget,Window,Node,ApplicationCache,AudioTrackList,BroadcastChannel,ChannelMergerNode,CryptoOperation,EventSource,FileReader,HTMLUnknownElement,IDBDatabase,IDBRequest,IDBTransaction,KeyOperation,MediaController,MessagePort,ModalWindow,Notification,SVGElementInstance,Screen,SharedWorker,TextTrack,TextTrackCue,TextTrackList,WebSocket,WebSocketWorker,Worker,XMLHttpRequest,XMLHttpRequestEventTarget,XMLHttpRequestUpload".split(
  ","
);
const INTEGRATION_NAME = "BrowserApiErrors";
const _browserApiErrorsIntegration = ((options = {}) => {
  const _options = {
    XMLHttpRequest: true,
    eventTarget: true,
    requestAnimationFrame: true,
    setInterval: true,
    setTimeout: true,
    unregisterOriginalCallbacks: false,
    ...options
  };
  return {
    name: INTEGRATION_NAME,
    // TODO: This currently only works for the first client this is setup
    // We may want to adjust this to check for client etc.
    setupOnce() {
      if (_options.setTimeout) {
        core.fill(helpers.WINDOW, "setTimeout", _wrapTimeFunction);
      }
      if (_options.setInterval) {
        core.fill(helpers.WINDOW, "setInterval", _wrapTimeFunction);
      }
      if (_options.requestAnimationFrame) {
        core.fill(helpers.WINDOW, "requestAnimationFrame", _wrapRAF);
      }
      if (_options.XMLHttpRequest && "XMLHttpRequest" in helpers.WINDOW) {
        core.fill(XMLHttpRequest.prototype, "send", _wrapXHR);
      }
      const eventTargetOption = _options.eventTarget;
      if (eventTargetOption) {
        const eventTarget = Array.isArray(eventTargetOption) ? eventTargetOption : DEFAULT_EVENT_TARGET;
        eventTarget.forEach((target) => _wrapEventTarget(target, _options));
      }
    }
  };
});
const browserApiErrorsIntegration = core.defineIntegration(_browserApiErrorsIntegration);
function _wrapTimeFunction(original) {
  return function(...args) {
    const originalCallback = args[0];
    args[0] = helpers.wrap(originalCallback, {
      mechanism: {
        handled: false,
        type: `auto.browser.browserapierrors.${core.getFunctionName(original)}`
      }
    });
    return original.apply(this, args);
  };
}
function _wrapRAF(original) {
  return function(callback) {
    return original.apply(this, [
      helpers.wrap(callback, {
        mechanism: {
          data: {
            handler: core.getFunctionName(original)
          },
          handled: false,
          type: "auto.browser.browserapierrors.requestAnimationFrame"
        }
      })
    ]);
  };
}
function _wrapXHR(originalSend) {
  return function(...args) {
    const xhr = this;
    const xmlHttpRequestProps = ["onload", "onerror", "onprogress", "onreadystatechange"];
    xmlHttpRequestProps.forEach((prop) => {
      if (prop in xhr && typeof xhr[prop] === "function") {
        core.fill(xhr, prop, function(original) {
          const wrapOptions = {
            mechanism: {
              data: {
                handler: core.getFunctionName(original)
              },
              handled: false,
              type: `auto.browser.browserapierrors.xhr.${prop}`
            }
          };
          const originalFunction = core.getOriginalFunction(original);
          if (originalFunction) {
            wrapOptions.mechanism.data.handler = core.getFunctionName(originalFunction);
          }
          return helpers.wrap(original, wrapOptions);
        });
      }
    });
    return originalSend.apply(this, args);
  };
}
function _wrapEventTarget(target, integrationOptions) {
  const globalObject = helpers.WINDOW;
  const proto = globalObject[target]?.prototype;
  if (!proto?.hasOwnProperty?.("addEventListener")) {
    return;
  }
  core.fill(proto, "addEventListener", function(original) {
    return function(eventName, fn, options) {
      try {
        if (isEventListenerObject(fn)) {
          fn.handleEvent = helpers.wrap(fn.handleEvent, {
            mechanism: {
              data: {
                handler: core.getFunctionName(fn),
                target
              },
              handled: false,
              type: "auto.browser.browserapierrors.handleEvent"
            }
          });
        }
      } catch {
      }
      if (integrationOptions.unregisterOriginalCallbacks) {
        unregisterOriginalCallback(this, eventName, fn);
      }
      return original.apply(this, [
        eventName,
        helpers.wrap(fn, {
          mechanism: {
            data: {
              handler: core.getFunctionName(fn),
              target
            },
            handled: false,
            type: "auto.browser.browserapierrors.addEventListener"
          }
        }),
        options
      ]);
    };
  });
  core.fill(proto, "removeEventListener", function(originalRemoveEventListener) {
    return function(eventName, fn, options) {
      try {
        if (Object.prototype.hasOwnProperty.call(fn, "__sentry_wrapped__")) {
          const originalEventHandler = fn.__sentry_wrapped__;
          if (originalEventHandler) {
            originalRemoveEventListener.call(this, eventName, originalEventHandler, options);
          }
        }
      } catch {
      }
      return originalRemoveEventListener.call(this, eventName, fn, options);
    };
  });
}
function isEventListenerObject(obj) {
  return typeof obj.handleEvent === "function";
}
function unregisterOriginalCallback(target, eventName, fn) {
  if (target && typeof target === "object" && "removeEventListener" in target && typeof target.removeEventListener === "function") {
    target.removeEventListener(eventName, fn);
  }
}

exports.browserApiErrorsIntegration = browserApiErrorsIntegration;
//# sourceMappingURL=browserapierrors.js.map
