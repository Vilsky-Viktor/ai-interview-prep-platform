import { isAlreadyCaptured, getIsolationScope, withScope, httpRequestToRequestData, captureException } from '@sentry/core';
import { waitUntil, flushSafelyWithTimeout } from '../utils/responseEnd.js';

async function captureUnderscoreErrorException(contextOrProps) {
  const { req, res, err } = contextOrProps;
  const statusCode = res?.statusCode || contextOrProps.statusCode;
  if (statusCode && statusCode < 500) {
    return;
  }
  if (!contextOrProps.pathname) {
    return;
  }
  if (err && isAlreadyCaptured(err)) {
    waitUntil(flushSafelyWithTimeout());
    const storedEventId = typeof err === "object" ? err.__sentry_event_id__ : void 0;
    if (typeof storedEventId === "string") {
      getIsolationScope().setLastEventId(storedEventId);
      return storedEventId;
    }
    return getIsolationScope().lastEventId();
  }
  const eventId = withScope((scope) => {
    if (req) {
      const normalizedRequest = httpRequestToRequestData(req);
      scope.setSDKProcessingMetadata({ normalizedRequest });
    }
    return captureException(err || `_error.js called with falsy error (${err})`, {
      mechanism: {
        type: "auto.function.nextjs.underscore_error",
        handled: false,
        data: {
          function: "_error.getInitialProps"
        }
      }
    });
  });
  waitUntil(flushSafelyWithTimeout());
  return eventId;
}

export { captureUnderscoreErrorException };
//# sourceMappingURL=_error.js.map
