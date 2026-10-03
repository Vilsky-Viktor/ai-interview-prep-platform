import { httpRequestToRequestData, getCurrentScope, getIsolationScope, getActiveSpan, getRootSpan, getTraceData, captureException } from '@sentry/core';
import { TRANSACTION_ATTR_SENTRY_ROUTE_BACKFILL } from '../span-attributes-with-logic-attached.js';

function withErrorInstrumentation(origFunction) {
  return async function(...origFunctionArguments) {
    try {
      return await origFunction.apply(this, origFunctionArguments);
    } catch (e) {
      captureException(e, {
        // TODO: check if origFunction.name actually returns the correct name or minified garbage
        // in this case, we can add another argument to this wrapper with the respective function name
        mechanism: { handled: false, type: "auto.function.nextjs.wrapped", data: { function: origFunction.name } }
      });
      throw e;
    }
  };
}
function withTracedServerSideDataFetcher(origDataFetcher, req, res, options) {
  return async function(...args) {
    const normalizedRequest = httpRequestToRequestData(req);
    getCurrentScope().setTransactionName(`${options.dataFetchingMethodName} (${options.dataFetcherRouteName})`);
    getIsolationScope().setSDKProcessingMetadata({ normalizedRequest });
    const span = getActiveSpan();
    if (span && options.requestedRouteName !== "/_error") {
      const root = getRootSpan(span);
      root.setAttribute(TRANSACTION_ATTR_SENTRY_ROUTE_BACKFILL, options.requestedRouteName);
    }
    const { "sentry-trace": sentryTrace, baggage } = getTraceData();
    return {
      sentryTrace,
      baggage,
      data: await origDataFetcher.apply(this, args)
    };
  };
}
async function callDataFetcherTraced(origFunction, origFunctionArgs) {
  try {
    return await origFunction(...origFunctionArgs);
  } catch (e) {
    captureException(e, { mechanism: { handled: false, type: "auto.function.nextjs.data_fetcher" } });
    throw e;
  }
}

export { callDataFetcherTraced, withErrorInstrumentation, withTracedServerSideDataFetcher };
//# sourceMappingURL=wrapperUtils.js.map
