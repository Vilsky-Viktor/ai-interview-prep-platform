import * as routeModule from '__SENTRY_WRAPPING_TARGET_FILE__';
export * from '__SENTRY_WRAPPING_TARGET_FILE__';
import * as Sentry from '@sentry/nextjs';

const userApiModule = routeModule;
let userProvidedHandler = void 0;
if ("default" in userApiModule && typeof userApiModule.default === "function") {
  userProvidedHandler = userApiModule.default;
} else if (typeof userApiModule === "function") {
  userProvidedHandler = userApiModule;
}
const origConfig = userApiModule.config || {};
const config = {
  ...origConfig,
  api: {
    ...origConfig.api,
    externalResolver: true
  }
};
let wrappedHandler = userProvidedHandler;
if (wrappedHandler && __VERCEL_CRONS_CONFIGURATION__) {
  wrappedHandler = Sentry.wrapApiHandlerWithSentryVercelCrons(wrappedHandler, __VERCEL_CRONS_CONFIGURATION__);
}
if (wrappedHandler) {
  wrappedHandler = Sentry.wrapApiHandlerWithSentry(wrappedHandler, "__ROUTE__");
}
const wrappedHandler_default = wrappedHandler;

export { config, wrappedHandler_default as default };
