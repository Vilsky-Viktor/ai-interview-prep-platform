import { defineIntegration, debug, isPlainObject, isError, addNonEnumerableProperty, getClient, isPrimitive, captureEvent, normalize } from '@sentry/core';
import { DEBUG_BUILD } from '../debug-build.js';
import { eventFromUnknownInput, extractType, extractMessage } from '../eventbuilder.js';
import { ignoreNextOnErrorMatching, WINDOW } from '../helpers.js';
import { _eventFromRejectionWithPrimitive, _enhanceEventWithInitialFrame, _getUnhandledRejectionError } from './globalhandlers.js';

const INTEGRATION_NAME = "WebWorker";
const MAX_FORWARDED_ERRORS = 20;
const webWorkerIntegration = defineIntegration(({ worker }) => ({
  name: INTEGRATION_NAME,
  setupOnce: () => {
    (Array.isArray(worker) ? worker : [worker]).forEach((w) => listenForSentryMessages(w));
  },
  addWorker: (worker2) => listenForSentryMessages(worker2)
}));
function listenForSentryMessages(worker) {
  const forwardedErrors = [];
  worker.addEventListener("error", ({ message, filename, lineno, colno }) => {
    const index = forwardedErrors.findIndex(
      (e) => e.message === message && e.url === filename && e.lineno === lineno && e.colno === colno
    );
    if (index !== -1) {
      forwardedErrors.splice(0, index + 1);
      ignoreNextOnErrorMatching({ msg: message, url: filename, line: lineno, column: colno });
    }
  });
  worker.addEventListener("message", (event) => {
    if (isSentryMessage(event.data)) {
      event.stopImmediatePropagation();
      if (event.data._sentryDebugIds) {
        DEBUG_BUILD && debug.log("Sentry debugId web worker message received", event.data);
        WINDOW._sentryDebugIds = {
          ...event.data._sentryDebugIds,
          // debugIds of the main thread have precedence over the worker's in case of a collision.
          ...WINDOW._sentryDebugIds
        };
      }
      if (event.data._sentryModuleMetadata) {
        DEBUG_BUILD && debug.log("Sentry module metadata web worker message received", event.data);
        WINDOW._sentryModuleMetadata = {
          ...event.data._sentryModuleMetadata,
          // Module metadata of the main thread have precedence over the worker's in case of a collision.
          ...WINDOW._sentryModuleMetadata
        };
      }
      if (event.data._sentryWasmImages) {
        DEBUG_BUILD && debug.log("Sentry WASM images web worker message received", event.data);
        const existingImages = WINDOW._sentryWasmImages || [];
        const newImages = event.data._sentryWasmImages.filter(
          (newImg) => isPlainObject(newImg) && typeof newImg.code_file === "string" && !existingImages.some((existing) => existing.code_file === newImg.code_file)
        );
        WINDOW._sentryWasmImages = [
          ...existingImages,
          ...newImages
        ];
      }
      if (event.data._sentryWorkerError) {
        DEBUG_BUILD && debug.log("Sentry worker error message received", event.data._sentryWorkerError);
        const { kind, message, url, lineno, colno } = event.data._sentryWorkerError;
        if (kind === "error") {
          if (forwardedErrors.push({ message, url, lineno, colno }) > MAX_FORWARDED_ERRORS) {
            forwardedErrors.shift();
          }
        }
        handleForwardedWorkerError(event.data._sentryWorkerError);
      }
    }
  });
}
function handleForwardedWorkerError(workerError) {
  const { reason, kind, name, filename, url, lineno, colno, plainError } = workerError;
  const isUnhandledRejection = kind !== "error";
  const error = plainError && isPlainObject(reason) ? errorFromPlain(reason) : reason;
  if (name && isError(error) && error.name !== name) {
    addNonEnumerableProperty(error, "name", name);
  }
  const client = getClient();
  if (!client) {
    return;
  }
  const { stackParser, attachStacktrace } = client.getOptions();
  const event = isUnhandledRejection && isPrimitive(error) ? _eventFromRejectionWithPrimitive(error) : eventFromUnknownInput(stackParser, error, void 0, attachStacktrace, isUnhandledRejection);
  if (!isUnhandledRejection) {
    _enhanceEventWithInitialFrame(event, url || filename, lineno, colno);
  }
  event.level = "error";
  if (filename) {
    event.contexts = {
      ...event.contexts,
      worker: {
        filename
      }
    };
  }
  captureEvent(event, {
    originalException: error,
    mechanism: {
      handled: false,
      type: isUnhandledRejection ? "auto.browser.web_worker.onunhandledrejection" : "auto.browser.web_worker.onerror"
    }
  });
  DEBUG_BUILD && debug.log(`Captured worker ${isUnhandledRejection ? "unhandled rejection" : "error"}`, error);
}
function registerWebWorker({ self }) {
  Error.stackTraceLimit = 50;
  self.postMessage({
    _sentryMessage: true,
    _sentryDebugIds: self._sentryDebugIds ?? void 0,
    _sentryModuleMetadata: self._sentryModuleMetadata ?? void 0
  });
  const forward = (serializedError) => {
    const { reason } = serializedError;
    DEBUG_BUILD && debug.log(`[Sentry Worker] Forwarding ${serializedError.kind} to parent`, serializedError);
    postSerializedWorkerError(self, {
      ...serializedError,
      filename: self.location?.href,
      name: isError(reason) ? extractType(reason) : void 0
    });
  };
  self.addEventListener("error", (event) => {
    const { error, message, filename, lineno, colno } = event;
    forward({ kind: "error", reason: error ?? message, message, url: filename, lineno, colno });
  });
  self.addEventListener("unhandledrejection", (event) => {
    forward({ kind: "unhandledrejection", reason: _getUnhandledRejectionError(event) });
  });
  DEBUG_BUILD && debug.log("[Sentry Worker] Registered worker with error and unhandled rejection handling");
}
function postSerializedWorkerError(self, serializedError) {
  try {
    self.postMessage({
      _sentryMessage: true,
      _sentryWorkerError: serializedError
    });
    return;
  } catch {
  }
  const { reason } = serializedError;
  const plainError = isError(reason);
  const plainReason = plainError ? { message: extractMessage(reason), stack: reason.stack } : normalize(reason);
  try {
    self.postMessage({
      _sentryMessage: true,
      _sentryWorkerError: { ...serializedError, reason: plainReason, plainError }
    });
  } catch {
  }
}
function errorFromPlain(plain) {
  const error = new Error(String(plain.message));
  error.stack = typeof plain.stack === "string" ? plain.stack : void 0;
  return error;
}
function isSentryMessage(eventData) {
  if (!isPlainObject(eventData) || eventData._sentryMessage !== true) {
    return false;
  }
  const hasDebugIds = "_sentryDebugIds" in eventData;
  const hasModuleMetadata = "_sentryModuleMetadata" in eventData;
  const hasWorkerError = "_sentryWorkerError" in eventData;
  const hasWasmImages = "_sentryWasmImages" in eventData;
  if (!hasDebugIds && !hasModuleMetadata && !hasWorkerError && !hasWasmImages) {
    return false;
  }
  if (hasDebugIds && !(isPlainObject(eventData._sentryDebugIds) || eventData._sentryDebugIds === void 0)) {
    return false;
  }
  if (hasModuleMetadata && !(isPlainObject(eventData._sentryModuleMetadata) || eventData._sentryModuleMetadata === void 0)) {
    return false;
  }
  if (hasWorkerError && !isPlainObject(eventData._sentryWorkerError)) {
    return false;
  }
  if (hasWasmImages && (!Array.isArray(eventData._sentryWasmImages) || !eventData._sentryWasmImages.every(
    (img) => isPlainObject(img) && typeof img.code_file === "string"
  ))) {
    return false;
  }
  return true;
}

export { INTEGRATION_NAME, registerWebWorker, webWorkerIntegration };
//# sourceMappingURL=webWorker.js.map
