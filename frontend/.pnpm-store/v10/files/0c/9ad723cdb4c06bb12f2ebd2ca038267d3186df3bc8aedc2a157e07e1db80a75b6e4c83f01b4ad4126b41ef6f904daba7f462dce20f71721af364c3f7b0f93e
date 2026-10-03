Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const isBuild = require('../utils/isBuild.js');
const wrapperUtils = require('../utils/wrapperUtils.js');

function wrapGetStaticPropsWithSentry(origGetStaticPropsa, _parameterizedRoute) {
  return new Proxy(origGetStaticPropsa, {
    apply: async (wrappingTarget, thisArg, args) => {
      if (isBuild.isBuild()) {
        return wrappingTarget.apply(thisArg, args);
      }
      const errorWrappedGetStaticProps = wrapperUtils.withErrorInstrumentation(wrappingTarget);
      return wrapperUtils.callDataFetcherTraced(errorWrappedGetStaticProps, args);
    }
  });
}

exports.wrapGetStaticPropsWithSentry = wrapGetStaticPropsWithSentry;
//# sourceMappingURL=wrapGetStaticPropsWithSentry.js.map
