Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');

function addHeadersAsAttributes(headers, span) {
  if (!headers) {
    return {};
  }
  const client = core.getClient();
  if (!client || client.getDataCollectionOptions().httpHeaders.request === false) {
    return {};
  }
  const headersDict = headers instanceof Headers || typeof headers === "object" && "get" in headers ? core.winterCGHeadersToDict(headers) : headers;
  const headerAttributes = core.httpHeadersToSpanAttributes(headersDict, client.getDataCollectionOptions());
  if (span) {
    span.setAttributes(headerAttributes);
  }
  return headerAttributes;
}

exports.addHeadersAsAttributes = addHeadersAsAttributes;
//# sourceMappingURL=addHeadersAsAttributes.js.map
