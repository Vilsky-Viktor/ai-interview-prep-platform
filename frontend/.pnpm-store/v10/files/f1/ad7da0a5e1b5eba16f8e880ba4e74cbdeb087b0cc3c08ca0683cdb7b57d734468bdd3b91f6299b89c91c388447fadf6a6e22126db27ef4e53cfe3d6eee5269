import { debug, getCurrentScope, getClient, lastEventId, getReportDialogEndpoint } from '@sentry/core';
import { DEBUG_BUILD } from './debug-build.js';
import { WINDOW } from './helpers.js';

function showReportDialog(options = {}) {
  const optionalDocument = WINDOW.document;
  const injectionPoint = optionalDocument?.head || optionalDocument?.body;
  if (!injectionPoint) {
    DEBUG_BUILD && debug.error("[showReportDialog] Global document not defined");
    return;
  }
  const scope = getCurrentScope();
  const client = getClient();
  const dsn = client?.getDsn();
  if (!dsn) {
    DEBUG_BUILD && debug.error("[showReportDialog] DSN not configured");
    return;
  }
  const mergedOptions = {
    ...options,
    user: {
      ...scope.getUser(),
      ...options.user
    },
    eventId: options.eventId || lastEventId()
  };
  const { onLoad, onClose, onError } = mergedOptions;
  if (!mergedOptions.eventId) {
    DEBUG_BUILD && debug.error("[showReportDialog] No event ID");
    onError?.(new Error("No event ID to show the report dialog for"));
    return;
  }
  const script = WINDOW.document.createElement("script");
  script.async = true;
  script.crossOrigin = "anonymous";
  script.src = getReportDialogEndpoint(dsn, mergedOptions);
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
          WINDOW.removeEventListener("message", reportDialogClosedMessageHandler);
        }
      }
    };
    WINDOW.addEventListener("message", reportDialogClosedMessageHandler);
    script.addEventListener("error", () => {
      WINDOW.removeEventListener("message", reportDialogClosedMessageHandler);
    });
  }
  injectionPoint.appendChild(script);
}

export { showReportDialog };
//# sourceMappingURL=report-dialog.js.map
