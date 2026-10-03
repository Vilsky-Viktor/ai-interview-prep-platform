Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const isBuild = require('../utils/isBuild.js');
const wrapperUtils = require('../utils/wrapperUtils.js');

function wrapDocumentGetInitialPropsWithSentry(origDocumentGetInitialProps) {
  return new Proxy(origDocumentGetInitialProps, {
    apply: async (wrappingTarget, thisArg, args) => {
      if (isBuild.isBuild()) {
        return wrappingTarget.apply(thisArg, args);
      }
      const [context] = args;
      const { req, res } = context;
      const errorWrappedGetInitialProps = wrapperUtils.withErrorInstrumentation(wrappingTarget);
      if (req && res) {
        const tracedGetInitialProps = wrapperUtils.withTracedServerSideDataFetcher(errorWrappedGetInitialProps, req, res, {
          dataFetcherRouteName: "/_document",
          requestedRouteName: context.pathname,
          dataFetchingMethodName: "getInitialProps"
        });
        const { data } = await tracedGetInitialProps.apply(thisArg, args);
        return data;
      } else {
        return errorWrappedGetInitialProps.apply(thisArg, args);
      }
    }
  });
}

exports.wrapDocumentGetInitialPropsWithSentry = wrapDocumentGetInitialPropsWithSentry;
//# sourceMappingURL=wrapDocumentGetInitialPropsWithSentry.js.map
