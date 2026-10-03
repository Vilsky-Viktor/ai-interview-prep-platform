Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const debugBuild = require('./debug-build.js');
const helpers = require('./helpers.js');

function showReportDialog(options = {}) {
  const optionalDocument = helpers.WINDOW.document;
  const injectionPoint = optionalDocument?.head || optionalDocument?.body;
  if (!injectionPoint) {
    debugBuild.DEBUG_BUILD && core.debug.error("[showReportDialog] Global document not defined");
    return;
  }
  const scope = core.getCurrentScope();
  const client = core.getClient();
  const dsn = client?.getDsn();
  if (!dsn) {
    debugBuild.DEBUG_BUILD && core.debug.error("[showReportDialog] DSN not configured");
    return;
  }
  const mergedOptions = {
    ...options,
    user: {
      ...scope.getUser(),
      ...options.user
    },
    eventId: options.eventId || core.lastEventId()
  };
  const { onLoad, onClose, onError } = mergedOptions;
  if (!mergedOptions.eventId) {
    debugBuild.DEBUG_BUILD && core.debug.error("[showReportDialog] No event ID");
    onError?.(new Error("No event ID to show the report dialog for"));
    return;
  }
  const script = helpers.WINDOW.document.createElement("script");
  script.async = true;
  script.crossOrigin = "anonymous";
  script.src = core.getReportDialogEndpoint(dsn, mergedOptions);
  if (onLoad) {
    script.onload = onLoad;
  }
  if (onError) {
    script.onerror = () => {
      onError(new Error("Failed to load the report dialog script"));
    };
  }
  if (onClose) {
    const reportDialogClosedMessageHandler = (event) => {
      if (event.data === "__sentry_reportdialog_closed__") {
        try {
          onClose();
        } finally {
          helpers.WINDOW.removeEventListener("message", reportDialogClosedMessageHandler);
        }
      }
    };
    helpers.WINDOW.addEventListener("message", reportDialogClosedMessageHandler);
    script.addEventListener("error", () => {
      helpers.WINDOW.removeEventListener("message", reportDialogClosedMessageHandler);
    });
  }
  injectionPoint.appendChild(script);
}

exports.showReportDialog = showReportDialog;
//# sourceMappingURL=report-dialog.js.map
