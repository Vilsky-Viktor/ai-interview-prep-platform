Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const debugBuild = require('../debug-build.js');
const helpers = require('../helpers.js');
const attributes = require('@sentry/conventions/attributes');

function registerBackgroundTabDetection() {
  if (helpers.WINDOW.document) {
    helpers.WINDOW.document.addEventListener("visibilitychange", () => {
      const activeSpan = core.getActiveSpan();
      if (!activeSpan) {
        return;
      }
      const rootSpan = core.getRootSpan(activeSpan);
      if (helpers.WINDOW.document.hidden && rootSpan) {
        const cancelledStatus = "cancelled";
        const {
          attributes: { [attributes.SENTRY_OP]: op },
          status
        } = core.spanToJSON(rootSpan);
        if (debugBuild.DEBUG_BUILD) {
          core.debug.log(`[Tracing] Transaction: ${cancelledStatus} -> since tab moved to the background, op: ${op}`);
        }
        if (status === "ok") {
          rootSpan.setStatus({ code: core.SPAN_STATUS_ERROR, message: cancelledStatus });
        }
        rootSpan.setAttribute("sentry.cancellation_reason", "document.hidden");
        rootSpan.end();
      }
    });
  } else {
    debugBuild.DEBUG_BUILD && core.debug.warn("[Tracing] Could not set up background tab detection due to lack of global document");
  }
}

exports.registerBackgroundTabDetection = registerBackgroundTabDetection;
//# sourceMappingURL=backgroundtab.js.map
