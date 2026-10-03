import { getClient, winterCGHeadersToDict, httpHeadersToSpanAttributes } from '@sentry/core';

function addHeadersAsAttributes(headers, span) {
  if (!headers) {
    return {};
  }
  const client = getClient();
  if (!client || client.getDataCollectionOptions().httpHeaders.request === false) {
    return {};
  }
  const headersDict = headers instanceof Headers || typeof headers === "object" && "get" in headers ? winterCGHeadersToDict(headers) : headers;
  const headerAttributes = httpHeadersToSpanAttributes(headersDict, client.getDataCollectionOptions());
  if (span) {
    span.setAttributes(headerAttributes);
  }
  return headerAttributes;
}

export { addHeadersAsAttributes };
//# sourceMappingURL=addHeadersAsAttributes.js.map
