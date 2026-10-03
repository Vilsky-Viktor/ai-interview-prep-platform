import * as origModule from '__SENTRY_NEXTJS_REQUEST_ASYNC_STORAGE_SHIM__';
import * as routeModule from '__SENTRY_WRAPPING_TARGET_FILE__';
export * from '__SENTRY_WRAPPING_TARGET_FILE__';
export { default } from '__SENTRY_WRAPPING_TARGET_FILE__';
import * as Sentry from '@sentry/nextjs';

const asyncStorageModule = { ...origModule };
const requestAsyncStorage = "workUnitAsyncStorage" in asyncStorageModule ? asyncStorageModule.workUnitAsyncStorage : "requestAsyncStorage" in asyncStorageModule ? asyncStorageModule.requestAsyncStorage : void 0;
function wrapHandler(handler, method) {
  if (process.env.NEXT_PHASE === "phase-production-build") {
    return handler;
  }
  if (typeof handler !== "function") {
    return handler;
  }
  return new Proxy(handler, {
    apply: (originalFunction, thisArg, args) => {
      let headers = void 0;
      try {
        const requestAsyncStore = requestAsyncStorage?.getStore();
        headers = requestAsyncStore?.headers;
      } catch {
      }
      return Sentry.wrapRouteHandlerWithSentry(originalFunction, {
        method,
        parameterizedRoute: "__ROUTE__",
        headers
      }).apply(thisArg, args);
    }
  });
}
const GET = wrapHandler(routeModule.GET, "GET");
const POST = wrapHandler(routeModule.POST, "POST");
const PUT = wrapHandler(routeModule.PUT, "PUT");
const PATCH = wrapHandler(routeModule.PATCH, "PATCH");
const DELETE = wrapHandler(routeModule.DELETE, "DELETE");
const HEAD = wrapHandler(routeModule.HEAD, "HEAD");
const OPTIONS = wrapHandler(routeModule.OPTIONS, "OPTIONS");

export { DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT };
