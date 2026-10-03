Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const browser = require('@sentry/browser');
const core = require('@sentry/core');

function setCause(error, cause) {
  const seenErrors = /* @__PURE__ */ new WeakSet();
  function recurse(error2, cause2) {
    if (seenErrors.has(error2)) {
      return;
    }
    if (error2.cause) {
      seenErrors.add(error2);
      return recurse(error2.cause, cause2);
    }
    error2.cause = cause2;
  }
  recurse(error, cause);
}
function captureReactException(error, { componentStack }, hint) {
  if (core.isError(error) && componentStack) {
    const errorBoundaryError = new Error(error.message);
    errorBoundaryError.name = `React ErrorBoundary ${error.name}`;
    errorBoundaryError.stack = componentStack;
    setCause(error, errorBoundaryError);
  }
  return browser.captureException(error, hint);
}
function reactErrorHandler(callback) {
  return (error, errorInfo) => {
    const hasCallback = !!callback;
    const eventId = captureReactException(error, errorInfo, {
      mechanism: { handled: hasCallback, type: "auto.function.react.error_handler" }
    });
    if (hasCallback) {
      callback(error, errorInfo, eventId);
    }
  };
}

exports.captureReactException = captureReactException;
exports.reactErrorHandler = reactErrorHandler;
exports.setCause = setCause;
//# sourceMappingURL=error.js.map
