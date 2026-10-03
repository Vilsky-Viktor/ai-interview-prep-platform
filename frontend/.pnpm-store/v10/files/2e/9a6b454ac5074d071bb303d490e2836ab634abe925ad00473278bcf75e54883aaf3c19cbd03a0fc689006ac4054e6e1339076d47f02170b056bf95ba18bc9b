Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const responseEnd = require('../utils/responseEnd.js');

async function captureUnderscoreErrorException(contextOrProps) {
  const { req, res, err } = contextOrProps;
  const statusCode = res?.statusCode || contextOrProps.statusCode;
  if (statusCode && statusCode < 500) {
    return;
  }
  if (!contextOrProps.pathname) {
    return;
  }
  if (err && core.isAlreadyCaptured(err)) {
    responseEnd.waitUntil(responseEnd.flushSafelyWithTimeout());
    const storedEventId = typeof err === "object" ? err.__sentry_event_id__ : void 0;
    if (typeof storedEventId === "string") {
      core.getIsolationScope().setLastEventId(storedEventId);
      return storedEventId;
    }
    return core.getIsolationScope().lastEventId();
  }
  const eventId = core.withScope((scope) => {
    if (req) {
      const normalizedRequest = core.httpRequestToRequestData(req);
      scope.setSDKProcessingMetadata({ normalizedRequest });
    }
    return core.captureException(err || `_error.js called with falsy error (${err})`, {
      mechanism: {
        type: "auto.function.nextjs.underscore_error",
        handled: false,
        data: {
          function: "_error.getInitialProps"
        }
      }
    });
  });
  responseEnd.waitUntil(responseEnd.flushSafelyWithTimeout());
  return eventId;
}

exports.captureUnderscoreErrorException = captureUnderscoreErrorException;
//# sourceMappingURL=_error.js.map
