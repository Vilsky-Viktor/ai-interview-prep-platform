import { isBuild } from '../utils/isBuild.js';
import { withTracedServerSideDataFetcher, withErrorInstrumentation } from '../utils/wrapperUtils.js';

function wrapAppGetInitialPropsWithSentry(origAppGetInitialProps) {
  return new Proxy(origAppGetInitialProps, {
    apply: async (wrappingTarget, thisArg, args) => {
      if (isBuild()) {
        return wrappingTarget.apply(thisArg, args);
      }
      const [context] = args;
      const { req, res } = context.ctx;
      const errorWrappedAppGetInitialProps = withErrorInstrumentation(wrappingTarget);
      if (req && res) {
        const tracedGetInitialProps = withTracedServerSideDataFetcher(errorWrappedAppGetInitialProps, req, res, {
          dataFetcherRouteName: "/_app",
          requestedRouteName: context.ctx.pathname,
          dataFetchingMethodName: "getInitialProps"
        });
        const {
          data: appGetInitialProps,
          sentryTrace,
          baggage
        } = await tracedGetInitialProps.apply(thisArg, args);
        if (typeof appGetInitialProps === "object" && appGetInitialProps !== null) {
          if (!appGetInitialProps.pageProps) {
            appGetInitialProps.pageProps = {};
          }
          if (sentryTrace) {
            appGetInitialProps.pageProps._sentryTraceData = sentryTrace;
          }
          if (baggage) {
            appGetInitialProps.pageProps._sentryBaggage = baggage;
          }
        }
        return appGetInitialProps;
      } else {
        return errorWrappedAppGetInitialProps.apply(thisArg, args);
      }
    }
  });
}

export { wrapAppGetInitialPropsWithSentry };
//# sourceMappingURL=wrapAppGetInitialPropsWithSentry.js.map
