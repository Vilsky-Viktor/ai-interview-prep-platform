import { isBuild } from '../utils/isBuild.js';
import { withTracedServerSideDataFetcher, withErrorInstrumentation } from '../utils/wrapperUtils.js';

function wrapGetInitialPropsWithSentry(origGetInitialProps) {
  return new Proxy(origGetInitialProps, {
    apply: async (wrappingTarget, thisArg, args) => {
      if (isBuild()) {
        return wrappingTarget.apply(thisArg, args);
      }
      const [context] = args;
      const { req, res } = context;
      const errorWrappedGetInitialProps = withErrorInstrumentation(wrappingTarget);
      if (req && res) {
        const tracedGetInitialProps = withTracedServerSideDataFetcher(errorWrappedGetInitialProps, req, res, {
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

export { wrapGetInitialPropsWithSentry };
//# sourceMappingURL=wrapGetInitialPropsWithSentry.js.map
