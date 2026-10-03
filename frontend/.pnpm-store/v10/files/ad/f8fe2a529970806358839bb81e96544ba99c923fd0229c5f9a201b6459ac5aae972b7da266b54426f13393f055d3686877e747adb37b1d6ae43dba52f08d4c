Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const attributes = require('@sentry/conventions/attributes');
const core = require('@sentry/core');

function backfillHttpServerStatus(span) {
  const spanJSON = core.spanToStaticSpanJSON(span);
  if (spanJSON.status !== "ok") {
    return;
  }
  const attributes$1 = spanJSON.data;
  const code = attributes$1[attributes.HTTP_RESPONSE_STATUS_CODE] ?? attributes$1[attributes.HTTP_STATUS_CODE];
  if (typeof code !== "number") {
    return;
  }
  const spanStatus = core.getSpanStatusFromHttpCode(code);
  if (spanStatus.code !== core.SPAN_STATUS_OK) {
    span.setStatus(spanStatus);
  }
}

exports.backfillHttpServerStatus = backfillHttpServerStatus;
//# sourceMappingURL=backfillHttpServerStatus.js.map
