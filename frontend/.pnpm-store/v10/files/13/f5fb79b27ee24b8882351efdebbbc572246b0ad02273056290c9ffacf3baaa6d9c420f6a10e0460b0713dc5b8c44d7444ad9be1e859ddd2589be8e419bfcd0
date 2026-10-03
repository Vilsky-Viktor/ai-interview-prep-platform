Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const isBuild = require('../utils/isBuild.js');
const wrapperUtils = require('../utils/wrapperUtils.js');

function wrapGetInitialPropsWithSentry(origGetInitialProps) {
  return new Proxy(origGetInitialProps, {
    apply: async (wrappingTarget, thisArg, args) => {
      if (isBuild.isBuild()) {
        return wrappingTarget.apply(thisArg, args);
      }
      const [context] = args;
      const { req, res } = context;
      const errorWrappedGetInitialProps = wrapperUtils.withErrorInstrumentation(wrappingTarget);
      if (req && res) {
        const tracedGetInitialProps = wrapperUtils.withTracedServerSideDataFetcher(errorWrappedGetInitialProps, req, res, {
          dataFetcherRouteName: context.pathname,
          requestedRouteName: context.pathname,
          dataFetchingMethodName: "getInitialProps"
        });
        const {
          data: initialProps,
          baggage,
          sentryTrace
        } = await tracedGetInitialProps.apply(thisArg, args) ?? {};
        if (typeof initialProps === "object" && initialProps !== null) {
          if (sentryTrace) {
            initialProps._sentryTraceData = sentryTrace;
          }
          if (baggage) {
            initialProps._sentryBaggage = baggage;
          }
        }
        return initialProps;
      } else {
        return errorWrappedGetInitialProps.apply(thisArg, args);
      }
    }
  });
}

exports.wrapGetInitialPropsWithSentry = wrapGetInitialPropsWithSentry;
//# sourceMappingURL=wrapGetInitialPropsWithSentry.js.map
