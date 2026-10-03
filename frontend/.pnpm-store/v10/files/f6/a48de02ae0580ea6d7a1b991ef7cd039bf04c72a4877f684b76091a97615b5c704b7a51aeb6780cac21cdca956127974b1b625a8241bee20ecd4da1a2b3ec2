import { DEBUG_BUILD } from '../../debug-build.js';
import { addNonEnumerableProperty } from '../../utils/object.js';
import { consoleSandbox } from '../../utils/debug-logger.js';
import { safeCallback } from '../../utils/safeCallback.js';

function withStaticSpan(callback) {
  addNonEnumerableProperty(callback, "_static", true);
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
  const modifiedSpan = safeCallback(
    DEBUG_BUILD ? "The `beforeSendSpan` callback threw an error, sending the span unmodified:" : "",
    () => beforeSendSpan(span),
    () => span
  );
  if (modifiedSpan) {
    return modifiedSpan;
  }
  if (!hasShownSpanDropWarning) {
    consoleSandbox(() => {
      console.warn(
        "[Sentry] Returning null from `beforeSendSpan` is disallowed. To drop certain spans, configure the respective integrations directly or use `ignoreSpans`."
      );
    });
    hasShownSpanDropWarning = true;
  }
  return span;
}

export { applyBeforeSendSpanCallback, isStaticBeforeSendSpanCallback, withStaticSpan, withStreamedSpan };
//# sourceMappingURL=beforeSendSpan.js.map
