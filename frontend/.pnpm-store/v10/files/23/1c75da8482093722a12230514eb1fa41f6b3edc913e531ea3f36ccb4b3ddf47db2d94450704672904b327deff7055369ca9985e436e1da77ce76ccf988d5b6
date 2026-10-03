Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const spanAttributesWithLogicAttached = require('../span-attributes-with-logic-attached.js');

function withErrorInstrumentation(origFunction) {
  return async function(...origFunctionArguments) {
    try {
      return await origFunction.apply(this, origFunctionArguments);
    } catch (e) {
      core.captureException(e, {
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
    const normalizedRequest = core.httpRequestToRequestData(req);
    core.getCurrentScope().setTransactionName(`${options.dataFetchingMethodName} (${options.dataFetcherRouteName})`);
    core.getIsolationScope().setSDKProcessingMetadata({ normalizedRequest });
    const span = core.getActiveSpan();
    if (span && options.requestedRouteName !== "/_error") {
      const root = core.getRootSpan(span);
      root.setAttribute(spanAttributesWithLogicAttached.TRANSACTION_ATTR_SENTRY_ROUTE_BACKFILL, options.requestedRouteName);
    }
    const { "sentry-trace": sentryTrace, baggage } = core.getTraceData();
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
    core.captureException(e, { mechanism: { handled: false, type: "auto.function.nextjs.data_fetcher" } });
    throw e;
  }
}

exports.callDataFetcherTraced = callDataFetcherTraced;
exports.withErrorInstrumentation = withErrorInstrumentation;
exports.withTracedServerSideDataFetcher = withTracedServerSideDataFetcher;
//# sourceMappingURL=wrapperUtils.js.map
