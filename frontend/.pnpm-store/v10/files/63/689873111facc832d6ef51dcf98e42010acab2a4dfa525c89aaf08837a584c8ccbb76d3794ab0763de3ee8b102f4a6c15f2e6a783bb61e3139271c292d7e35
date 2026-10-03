import { isBuild } from '../utils/isBuild.js';
import { withTracedServerSideDataFetcher, withErrorInstrumentation } from '../utils/wrapperUtils.js';

function wrapDocumentGetInitialPropsWithSentry(origDocumentGetInitialProps) {
  return new Proxy(origDocumentGetInitialProps, {
    apply: async (wrappingTarget, thisArg, args) => {
      if (isBuild()) {
        return wrappingTarget.apply(thisArg, args);
      }
      const [context] = args;
      const { req, res } = context;
      const errorWrappedGetInitialProps = withErrorInstrumentation(wrappingTarget);
      if (req && res) {
        const tracedGetInitialProps = withTracedServerSideDataFetcher(errorWrappedGetInitialProps, req, res, {
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

export { wrapDocumentGetInitialPropsWithSentry };
//# sourceMappingURL=wrapDocumentGetInitialPropsWithSentry.js.map
