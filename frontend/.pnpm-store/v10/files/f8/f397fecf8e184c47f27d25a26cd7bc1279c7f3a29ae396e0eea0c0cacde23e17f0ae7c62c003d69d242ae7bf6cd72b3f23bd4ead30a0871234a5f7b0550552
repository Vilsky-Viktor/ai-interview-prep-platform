Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const react = require('@sentry/react');
const nextRoutingInstrumentation = require('./routing/nextRoutingInstrumentation.js');

function browserTracingIntegration(options = {}) {
  const browserTracingIntegrationInstance = react.browserTracingIntegration({
    ...options,
    instrumentNavigation: false,
    instrumentPageLoad: false,
    onRequestSpanStart(...args) {
      const [span, { headers }] = args;
      if (headers?.get("next-router-prefetch")) {
        span?.setAttribute("http.request.prefetch", true);
      }
      return options.onRequestSpanStart?.(...args);
    }
  });
  const { instrumentPageLoad = true, instrumentNavigation = true } = options;
  return {
    ...browserTracingIntegrationInstance,
    afterAllSetup(client) {
      if (react.isBotUserAgent()) {
        return;
      }
      if (instrumentNavigation) {
        nextRoutingInstrumentation.nextRouterInstrumentNavigation(client);
      }
      browserTracingIntegrationInstance.afterAllSetup(client);
      if (instrumentPageLoad) {
        nextRoutingInstrumentation.nextRouterInstrumentPageLoad(client);
      }
    }
  };
}

exports.browserTracingIntegration = browserTracingIntegration;
//# sourceMappingURL=browserTracingIntegration.js.map
