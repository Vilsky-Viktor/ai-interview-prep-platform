import { HTTP_STATUS_CODE, HTTP_RESPONSE_STATUS_CODE } from '@sentry/conventions/attributes';

function backfillHttpResponseStatusCode(attributes) {
  const legacyHttpStatusCode = attributes[HTTP_STATUS_CODE];
  if (attributes[HTTP_RESPONSE_STATUS_CODE] === void 0 && legacyHttpStatusCode !== void 0) {
    attributes[HTTP_RESPONSE_STATUS_CODE] = legacyHttpStatusCode;
  }
}

export { backfillHttpResponseStatusCode };
//# sourceMappingURL=backfillHttpResponseStatusCode.js.map
