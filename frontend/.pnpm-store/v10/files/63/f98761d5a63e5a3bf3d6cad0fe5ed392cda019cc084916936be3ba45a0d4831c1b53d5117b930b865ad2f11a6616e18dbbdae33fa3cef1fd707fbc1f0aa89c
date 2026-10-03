Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const debugBuild = require('../../debug-build.js');
const object = require('../../utils/object.js');
const debugLogger = require('../../utils/debug-logger.js');
const safeCallback = require('../../utils/safeCallback.js');

function withStaticSpan(callback) {
  object.addNonEnumerableProperty(callback, "_static", true);
  return callback;
}
function withStreamedSpan(callback) {
  return callback;
}
function isStaticBeforeSendSpanCallback(callback) {
  return !!callback && typeof callback === "function" && "_static" in callback && !!callback._static;
}
let hasShownSpanDropWarning = false;
function applyBeforeSendSpanCallback(span, beforeSendSpan) {
  const modifiedSpan = safeCallback.safeCallback(
    debugBuild.DEBUG_BUILD ? "The `beforeSendSpan` callback threw an error, sending the span unmodified:" : "",
    () => beforeSendSpan(span),
    () => span
  );
  if (modifiedSpan) {
    return modifiedSpan;
  }
  if (!hasShownSpanDropWarning) {
    debugLogger.consoleSandbox(() => {
      console.warn(
        "[Sentry] Returning null from `beforeSendSpan` is disallowed. To drop certain spans, configure the respective integrations directly or use `ignoreSpans`."
      );
    });
    hasShownSpanDropWarning = true;
  }
  return span;
}

exports.applyBeforeSendSpanCallback = applyBeforeSendSpanCallback;
exports.isStaticBeforeSendSpanCallback = isStaticBeforeSendSpanCallback;
exports.withStaticSpan = withStaticSpan;
exports.withStreamedSpan = withStreamedSpan;
//# sourceMappingURL=beforeSendSpan.js.map
