Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const attributes = require('@sentry/conventions/attributes');

function backfillHttpResponseStatusCode(attributes$1) {
  const legacyHttpStatusCode = attributes$1[attributes.HTTP_STATUS_CODE];
  if (attributes$1[attributes.HTTP_RESPONSE_STATUS_CODE] === void 0 && legacyHttpStatusCode !== void 0) {
    attributes$1[attributes.HTTP_RESPONSE_STATUS_CODE] = legacyHttpStatusCode;
  }
}

exports.backfillHttpResponseStatusCode = backfillHttpResponseStatusCode;
//# sourceMappingURL=backfillHttpResponseStatusCode.js.map
