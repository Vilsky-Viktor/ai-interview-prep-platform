import { GLOBAL_OBJ, debug } from '@sentry/core';
import { DEBUG_BUILD } from '../common/debug-build.js';

function prepareSafeIdGeneratorContext() {
  const sym = /* @__PURE__ */ Symbol.for("__SENTRY_SAFE_RANDOM_ID_WRAPPER__");
  const globalWithSymbol = GLOBAL_OBJ;
  const initialSnapshot = getAsyncLocalStorageSnapshot();
  if (!initialSnapshot) {
    return;
  }
  let cachedSnapshot = initialSnapshot;
  globalWithSymbol[sym] = (callback) => {
    try {
      return cachedSnapshot(callback);
    } catch (error) {
      if (!isAsyncLocalStorageError(error)) {
        throw error;
      }
      const freshSnapshot = getAsyncLocalStorageSnapshot();
      if (!freshSnapshot) {
        return callback();
      }
      cachedSnapshot = freshSnapshot;
      try {
        return cachedSnapshot(callback);
      } catch (retryError) {
        if (!isAsyncLocalStorageError(retryError)) {
          throw retryError;
        }
        return callback();
      }
    }
  };
  DEBUG_BUILD && debug.log("[@sentry/nextjs] Prepared safe random ID generator context");
}
function getAsyncLocalStorage() {
  if (typeof AsyncLocalStorage !== "undefined") {
    return AsyncLocalStorage;
  }
  if ("getBuiltinModule" in process && typeof process.getBuiltinModule === "function") {
    const { AsyncLocalStorage: AsyncLocalStorage2 } = process.getBuiltinModule("async_hooks") ?? {};
    return AsyncLocalStorage2;
  }
  return void 0;
}
function getAsyncLocalStorageSnapshot() {
  const als = getAsyncLocalStorage();
  if (!als || typeof als.snapshot !== "function") {
    DEBUG_BUILD && debug.warn(
      "[@sentry/nextjs] No AsyncLocalStorage found in the runtime or AsyncLocalStorage.snapshot() is not available, skipping safe random ID generator context preparation, you may see some errors with cache components."
    );
    return void 0;
  }
  return als.snapshot();
}
function isAsyncLocalStorageError(error) {
  return error instanceof Error && error.message.includes("AsyncLocalStorage");
}

export { prepareSafeIdGeneratorContext };
//# sourceMappingURL=prepareSafeIdGeneratorContext.js.map
