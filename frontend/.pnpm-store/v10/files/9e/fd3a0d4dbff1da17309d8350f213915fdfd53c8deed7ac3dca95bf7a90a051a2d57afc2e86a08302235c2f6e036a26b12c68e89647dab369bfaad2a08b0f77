Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const isBuild = require('../utils/isBuild.js');
const wrapperUtils = require('../utils/wrapperUtils.js');

function wrapGetServerSidePropsWithSentry(origGetServerSideProps, parameterizedRoute) {
  return new Proxy(origGetServerSideProps, {
    apply: async (wrappingTarget, thisArg, args) => {
      if (isBuild.isBuild()) {
        return wrappingTarget.apply(thisArg, args);
      }
      const [context] = args;
      const { req, res } = context;
      const errorWrappedGetServerSideProps = wrapperUtils.withErrorInstrumentation(wrappingTarget);
      const tracedGetServerSideProps = wrapperUtils.withTracedServerSideDataFetcher(errorWrappedGetServerSideProps, req, res, {
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

exports.wrapGetServerSidePropsWithSentry = wrapGetServerSidePropsWithSentry;
//# sourceMappingURL=wrapGetServerSidePropsWithSentry.js.map
