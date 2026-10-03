import { browserTracingIntegration as browserTracingIntegration$1, isBotUserAgent } from '@sentry/react';
import { nextRouterInstrumentNavigation, nextRouterInstrumentPageLoad } from './routing/nextRoutingInstrumentation.js';

function browserTracingIntegration(options = {}) {
  const browserTracingIntegrationInstance = browserTracingIntegration$1({
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
      if (isBotUserAgent()) {
        return;
      }
      if (instrumentNavigation) {
        nextRouterInstrumentNavigation(client);
      }
      browserTracingIntegrationInstance.afterAllSetup(client);
      if (instrumentPageLoad) {
        nextRouterInstrumentPageLoad(client);
      }
    }
  };
}

export { browserTracingIntegration };
//# sourceMappingURL=browserTracingIntegration.js.map
