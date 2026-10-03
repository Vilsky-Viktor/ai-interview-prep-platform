import { HTTP_RESPONSE_STATUS_CODE, HTTP_STATUS_CODE } from '@sentry/conventions/attributes';
import { spanToStaticSpanJSON, getSpanStatusFromHttpCode, SPAN_STATUS_OK } from '@sentry/core';

function backfillHttpServerStatus(span) {
  const spanJSON = spanToStaticSpanJSON(span);
  if (spanJSON.status !== "ok") {
    return;
  }
  const attributes = spanJSON.data;
  const code = attributes[HTTP_RESPONSE_STATUS_CODE] ?? attributes[HTTP_STATUS_CODE];
  if (typeof code !== "number") {
    return;
  }
  const spanStatus = getSpanStatusFromHttpCode(code);
  if (spanStatus.code !== SPAN_STATUS_OK) {
    span.setStatus(spanStatus);
  }
}

export { backfillHttpServerStatus };
//# sourceMappingURL=backfillHttpServerStatus.js.map
