import { isBuild } from '../utils/isBuild.js';
import { callDataFetcherTraced, withErrorInstrumentation } from '../utils/wrapperUtils.js';

function wrapGetStaticPropsWithSentry(origGetStaticPropsa, _parameterizedRoute) {
  return new Proxy(origGetStaticPropsa, {
    apply: async (wrappingTarget, thisArg, args) => {
      if (isBuild()) {
        return wrappingTarget.apply(thisArg, args);
      }
      const errorWrappedGetStaticProps = withErrorInstrumentation(wrappingTarget);
      return callDataFetcherTraced(errorWrappedGetStaticProps, args);
    }
  });
}

export { wrapGetStaticPropsWithSentry };
//# sourceMappingURL=wrapGetStaticPropsWithSentry.js.map
