Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');

function generateRandomTunnelRoute() {
  const randomString = core._INTERNAL_safeMathRandom().toString(36).substring(2, 10);
  return `/${randomString}`;
}
function resolveTunnelRoute(tunnelRoute) {
  if (process.env.__SENTRY_TUNNEL_ROUTE__) {
    return process.env.__SENTRY_TUNNEL_ROUTE__;
  }
  const resolvedTunnelRoute = typeof tunnelRoute === "string" ? tunnelRoute : generateRandomTunnelRoute();
  if (resolvedTunnelRoute) {
    process.env.__SENTRY_TUNNEL_ROUTE__ = resolvedTunnelRoute;
  }
  return resolvedTunnelRoute;
}
function setUpTunnelRewriteRules(userNextConfig, tunnelPath) {
  const originalRewrites = userNextConfig.rewrites;
  const destinationOverride = process.env._SENTRY_TUNNEL_DESTINATION_OVERRIDE;
  const destination = destinationOverride || "https://o:orgid.ingest.sentry.io/api/:projectid/envelope/?hsts=0";
  const destinationWithRegion = destinationOverride || "https://o:orgid.ingest.:region.sentry.io/api/:projectid/envelope/?hsts=0";
  userNextConfig.rewrites = async (...args) => {
    const tunnelRouteRewrite = {
      // Matched rewrite routes will look like the following: `[tunnelPath]?o=[orgid]&p=[projectid]`
      // Nextjs will automatically convert `source` into a regex for us
      source: `${tunnelPath}(/?)`,
      has: [
        {
          type: "query",
          key: "o",
          // short for orgId - we keep it short so matching is harder for ad-blockers
          value: "(?<orgid>\\d*)"
        },
        {
          type: "query",
          key: "p",
          // short for projectId - we keep it short so matching is harder for ad-blockers
          value: "(?<projectid>\\d*)"
        }
      ],
      destination
    };
    const tunnelRouteRewriteWithRegion = {
      // Matched rewrite routes will look like the following: `[tunnelPath]?o=[orgid]&p=[projectid]?r=[region]`
      // Nextjs will automatically convert `source` into a regex for us
      source: `${tunnelPath}(/?)`,
      has: [
        {
          type: "query",
          key: "o",
          // short for orgId - we keep it short so matching is harder for ad-blockers
          value: "(?<orgid>\\d*)"
        },
        {
          type: "query",
          key: "p",
          // short for projectId - we keep it short so matching is harder for ad-blockers
          value: "(?<projectid>\\d*)"
        },
        {
          type: "query",
          key: "r",
          // short for region - we keep it short so matching is harder for ad-blockers
          value: "(?<region>[a-z]{2})"
        }
      ],
      destination: destinationWithRegion
    };
    const newRewrites = [tunnelRouteRewriteWithRegion, tunnelRouteRewrite];
    if (typeof originalRewrites !== "function") {
      return newRewrites;
    }
    const originalRewritesResult = await originalRewrites(...args);
    if (Array.isArray(originalRewritesResult)) {
      return [...newRewrites, ...originalRewritesResult];
    } else {
      return {
        ...originalRewritesResult,
        beforeFiles: [...newRewrites, ...originalRewritesResult.beforeFiles || []]
      };
    }
  };
}

exports.resolveTunnelRoute = resolveTunnelRoute;
exports.setUpTunnelRewriteRules = setUpTunnelRewriteRules;
//# sourceMappingURL=tunnel.js.map
