import { isBuild } from '../utils/isBuild.js';
import { withTracedServerSideDataFetcher, withErrorInstrumentation } from '../utils/wrapperUtils.js';

function wrapGetServerSidePropsWithSentry(origGetServerSideProps, parameterizedRoute) {
  return new Proxy(origGetServerSideProps, {
    apply: async (wrappingTarget, thisArg, args) => {
      if (isBuild()) {
        return wrappingTarget.apply(thisArg, args);
      }
      const [context] = args;
      const { req, res } = context;
      const errorWrappedGetServerSideProps = withErrorInstrumentation(wrappingTarget);
      const tracedGetServerSideProps = withTracedServerSideDataFetcher(errorWrappedGetServerSideProps, req, res, {
        dataFetcherRouteName: parameterizedRoute,
        requestedRouteName: parameterizedRoute,
        dataFetchingMethodName: "getServerSideProps"
      });
      const {
        data: serverSideProps,
        baggage,
        sentryTrace
      } = await tracedGetServerSideProps.apply(thisArg, args);
      if (typeof serverSideProps === "object" && serverSideProps !== null && "props" in serverSideProps) {
        if (sentryTrace) {
          serverSideProps.props._sentryTraceData = sentryTrace;
        }
        if (baggage) {
          serverSideProps.props._sentryBaggage = baggage;
        }
      }
      return serverSideProps;
    }
  });
}

export { wrapGetServerSidePropsWithSentry };
//# sourceMappingURL=wrapGetServerSidePropsWithSentry.js.map
