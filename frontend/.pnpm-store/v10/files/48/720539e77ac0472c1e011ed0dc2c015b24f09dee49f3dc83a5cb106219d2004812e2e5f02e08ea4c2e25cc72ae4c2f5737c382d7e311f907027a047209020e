Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const types = require('../types.js');

function addPageListener(type, listener, options) {
  if (types.WINDOW.document) {
    types.WINDOW.addEventListener(type, listener, options);
  }
}
function removePageListener(type, listener, options) {
  if (types.WINDOW.document) {
    types.WINDOW.removeEventListener(type, listener, options);
  }
}
const getNavigationEntry = (checkResponseStart = true) => {
  const navigationEntry = types.WINDOW.performance?.getEntriesByType?.("navigation")[0];
  if (
    // sentry-specific change:
    // We don't want to check for responseStart for our own use of `getNavigationEntry`
    !checkResponseStart || navigationEntry && navigationEntry.responseStart > 0 && navigationEntry.responseStart < performance.now()
  ) {
    return navigationEntry;
  }
};
const getActivationStart = () => {
  const navEntry = getNavigationEntry();
  return navEntry?.activationStart ?? 0;
};
const onHidden = (cb) => {
  const onHiddenCallback = (event) => {
    if (types.WINDOW.document?.visibilityState === "hidden") {
      cb(event);
    }
  };
  addPageListener("visibilitychange", onHiddenCallback, { capture: true });
};
let firstHiddenTime = -1;
const onHiddenFunctions = /* @__PURE__ */ new Set();
const initHiddenTime = () => {
  return types.WINDOW.document?.visibilityState === "hidden" && !types.WINDOW.document?.prerendering ? 0 : Infinity;
};
const onVisibilityUpdate = (event) => {
  if (types.WINDOW.document?.visibilityState === "hidden" && firstHiddenTime > -1) {
    if (event.type === "visibilitychange") {
      for (const onHiddenFunction of onHiddenFunctions) {
        onHiddenFunction();
      }
    }
    if (!isFinite(firstHiddenTime)) {
      firstHiddenTime = event.type === "visibilitychange" ? event.timeStamp : 0;
      removePageListener("prerenderingchange", onVisibilityUpdate, true);
    }
  }
};
const getVisibilityWatcher = () => {
  if (types.WINDOW.document && firstHiddenTime < 0) {
    const activationStart = getActivationStart();
    const firstVisibilityStateHiddenTime = !types.WINDOW.document.prerendering ? globalThis.performance.getEntriesByType("visibility-state").filter((e) => e.name === "hidden" && e.startTime > activationStart)[0]?.startTime : void 0;
    firstHiddenTime = firstVisibilityStateHiddenTime ?? initHiddenTime();
    addPageListener("visibilitychange", onVisibilityUpdate, true);
    addPageListener("prerenderingchange", onVisibilityUpdate, true);
  }
  return {
    get firstHiddenTime() {
      return firstHiddenTime;
    },
    onHidden(cb) {
      onHiddenFunctions.add(cb);
    }
  };
};
const whenIdleOrHidden = (cb) => {
  const rIC = types.WINDOW.requestIdleCallback || types.WINDOW.setTimeout;
  if (types.WINDOW.document?.visibilityState === "hidden") {
    cb();
  } else {
    let called = false;
    const runOnce = () => {
      if (!called) {
        cb();
        called = true;
      }
    };
    addPageListener("visibilitychange", runOnce, { once: true, capture: true });
    rIC(() => {
      runOnce();
      removePageListener("visibilitychange", runOnce, { capture: true });
    });
  }
};

exports.addPageListener = addPageListener;
exports.getActivationStart = getActivationStart;
exports.getNavigationEntry = getNavigationEntry;
exports.getVisibilityWatcher = getVisibilityWatcher;
exports.onHidden = onHidden;
exports.removePageListener = removePageListener;
exports.whenIdleOrHidden = whenIdleOrHidden;
//# sourceMappingURL=utils.js.map
