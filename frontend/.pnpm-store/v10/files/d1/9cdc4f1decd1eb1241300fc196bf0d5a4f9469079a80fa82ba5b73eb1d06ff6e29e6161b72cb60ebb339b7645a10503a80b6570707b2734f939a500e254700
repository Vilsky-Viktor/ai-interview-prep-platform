import * as routeModule from '__SENTRY_WRAPPING_TARGET_FILE__';
export * from '__SENTRY_WRAPPING_TARGET_FILE__';
import * as Sentry from '@sentry/nextjs';

const userApiModule = routeModule;
let userProvidedNamedHandler = void 0;
let userProvidedDefaultHandler = void 0;
let userProvidedMiddleware = false;
let userProvidedProxy = false;
if ("middleware" in userApiModule && typeof userApiModule.middleware === "function") {
  userProvidedNamedHandler = userApiModule.middleware;
  userProvidedMiddleware = true;
} else if ("proxy" in userApiModule && typeof userApiModule.proxy === "function") {
  userProvidedNamedHandler = userApiModule.proxy;
  userProvidedProxy = true;
} else if ("default" in userApiModule && typeof userApiModule.default === "function") {
  userProvidedDefaultHandler = userApiModule.default;
} else if (typeof userApiModule === "function") {
  userProvidedDefaultHandler = userApiModule;
}
const wrappedHandler = userProvidedNamedHandler ? Sentry.wrapMiddlewareWithSentry(userProvidedNamedHandler) : void 0;
const middleware = userProvidedMiddleware ? wrappedHandler : void 0;
const proxy = userProvidedProxy ? wrappedHandler : void 0;
const middlewareWrapperTemplate = userProvidedDefaultHandler ? Sentry.wrapMiddlewareWithSentry(userProvidedDefaultHandler) : void 0;

export { middlewareWrapperTemplate as default, middleware, proxy };
