import { isBuild } from '../utils/isBuild.js';
import { withTracedServerSideDataFetcher, withErrorInstrumentation } from '../utils/wrapperUtils.js';

function wrapErrorGetInitialPropsWithSentry(origErrorGetInitialProps) {
  return new Proxy(origErrorGetInitialProps, {
    apply: async (wrappingTarget, thisArg, args) => {
      if (isBuild()) {
        return wrappingTarget.apply(thisArg, args);
      }
      const [context] = args;
      const { req, res } = context;
      const errorWrappedGetInitialProps = withErrorInstrumentation(wrappingTarget);
      if (req && res) {
        const tracedGetInitialProps = withTracedServerSideDataFetcher(errorWrappedGetInitialProps, req, res, {
          dataFetcherRouteName: "/_error",
          requestedRouteName: context.pathname,
          dataFetchingMethodName: "getInitialProps"
        });
        const {
          data: errorGetInitialProps,
          baggage,
          sentryTrace
        } = await tracedGetInitialProps.apply(thisArg, args);
        if (typeof errorGetInitialProps === "object" && errorGetInitialProps !== null) {
          if (sentryTrace) {
            errorGetInitialProps._sentryTraceData = sentryTrace;
          }
          if (baggage) {
            errorGetInitialProps._sentryBaggage = baggage;
          }
        }
        return errorGetInitialProps;
      } else {
        return errorWrappedGetInitialProps.apply(thisArg, args);
      }
    }
  });
}

export { wrapErrorGetInitialPropsWithSentry };
//# sourceMappingURL=wrapErrorGetInitialPropsWithSentry.js.map
