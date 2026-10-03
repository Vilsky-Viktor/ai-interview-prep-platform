Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const path = require('path');
const util = require('../util.js');

function generateValueInjectionRules({
  routeManifest,
  nextJsVersion,
  tunnelPath,
  vercelCronsConfig
}) {
  const rules = [];
  const isomorphicValues = {};
  let clientValues = {};
  let serverValues = {};
  if (nextJsVersion) {
    isomorphicValues._sentryNextJsVersion = nextJsVersion;
  }
  if (routeManifest) {
    clientValues._sentryRouteManifest = JSON.stringify(routeManifest);
  }
  if (tunnelPath) {
    isomorphicValues._sentryRewritesTunnelPath = tunnelPath;
  }
  if (vercelCronsConfig) {
    serverValues._sentryVercelCronsConfig = JSON.stringify(vercelCronsConfig);
  }
  serverValues.__SENTRY_SERVER_MODULES__ = util.getPackageModules(process.cwd());
  if (Object.keys(isomorphicValues).length > 0) {
    clientValues = { ...clientValues, ...isomorphicValues };
    serverValues = { ...serverValues, ...isomorphicValues };
  }
  const hasConditionSupport = nextJsVersion ? util.supportsTurbopackRuleCondition(nextJsVersion) : false;
  if (Object.keys(clientValues).length > 0) {
    rules.push({
      matcher: "**/instrumentation-client.*",
      rule: {
        // Only run on user code, not node_modules or Next.js internals
        // condition field is only supported in Next.js 16+
        ...hasConditionSupport ? { condition: { not: "foreign" } } : {},
        loaders: [
          {
            loader: path.resolve(__dirname, "..", "loaders", "valueInjectionLoader.js"),
            options: {
              values: clientValues
            }
          }
        ]
      }
    });
  }
  if (Object.keys(serverValues).length > 0) {
    rules.push({
      matcher: "**/instrumentation.*",
      rule: {
        // Only run on user code, not node_modules or Next.js internals
        // condition field is only supported in Next.js 16+
        ...hasConditionSupport ? { condition: { not: "foreign" } } : {},
        loaders: [
          {
            loader: path.resolve(__dirname, "..", "loaders", "valueInjectionLoader.js"),
            options: {
              values: serverValues
            }
          }
        ]
      }
    });
  }
  return rules;
}

exports.generateValueInjectionRules = generateValueInjectionRules;
//# sourceMappingURL=generateValueInjectionRules.js.map
