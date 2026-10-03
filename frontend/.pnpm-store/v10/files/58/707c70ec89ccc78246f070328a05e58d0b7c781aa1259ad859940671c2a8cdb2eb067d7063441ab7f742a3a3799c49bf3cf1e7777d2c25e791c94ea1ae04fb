Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const browserUtils = require('@sentry/browser-utils');
const debugBuild = require('../debug-build.js');
const helpers = require('../helpers.js');

const browserSessionIntegration = core.defineIntegration((options = {}) => {
  const lifecycle = options.lifecycle ?? "page";
  return {
    name: "BrowserSession",
    setupOnce() {
      if (typeof helpers.WINDOW.document === "undefined") {
        debugBuild.DEBUG_BUILD && core.debug.warn("Using the `browserSessionIntegration` in non-browser environments is not supported.");
        return;
      }
      core.startSession({ ignoreDuration: true });
      let initialSessionSent = false;
      browserUtils.whenIdleOrHidden(() => {
        if (!initialSessionSent) {
          core.captureSession();
          initialSessionSent = true;
        }
      });
      const isolationScope = core.getIsolationScope();
      let previousUser = isolationScope.getUser();
      isolationScope.addScopeListener((scope) => {
        const maybeNewUser = scope.getUser();
        if (previousUser?.id !== maybeNewUser?.id || previousUser?.ip_address !== maybeNewUser?.ip_address) {
          previousUser = maybeNewUser;
          if (initialSessionSent) {
            core.captureSession();
          }
        }
      });
      if (lifecycle === "route") {
        browserUtils.addHistoryInstrumentationHandler(({ from, to }) => {
          if (from !== to) {
            core.startSession({ ignoreDuration: true });
            core.captureSession();
            initialSessionSent = true;
          }
        });
      }
    }
  };
});

exports.browserSessionIntegration = browserSessionIntegration;
//# sourceMappingURL=browsersession.js.map
