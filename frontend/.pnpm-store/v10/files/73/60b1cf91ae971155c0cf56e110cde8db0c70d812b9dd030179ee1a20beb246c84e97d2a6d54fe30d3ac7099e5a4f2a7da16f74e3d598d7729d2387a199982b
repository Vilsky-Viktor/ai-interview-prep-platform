Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const browserUtils = require('@sentry/browser-utils');

const WINDOW = core.GLOBAL_OBJ;
let ignoreOnError = 0;
const ignoredErrorReports = [];
function shouldIgnoreOnError(data) {
  if (ignoreOnError > 0) {
    return true;
  }
  const index = data ? ignoredErrorReports.findIndex((report) => isSameErrorReport(report, data)) : -1;
  if (index === -1) {
    return false;
  }
  ignoredErrorReports.splice(index, 1);
  return true;
}
function ignoreNextOnErrorMatching(report) {
  ignoredErrorReports.push(report);
  setTimeout(() => {
    const index = ignoredErrorReports.indexOf(report);
    if (index !== -1) {
      ignoredErrorReports.splice(index, 1);
    }
  });
}
function isSameErrorReport(a, b) {
  return a.msg === b.msg && a.url === b.url && a.line === b.line && a.column === b.column;
}
function ignoreNextOnError() {
  ignoreOnError++;
  setTimeout(() => {
    ignoreOnError--;
  });
}
function wrap(fn, options = {}) {
  function isFunction(fn2) {
    return typeof fn2 === "function";
  }
  if (!isFunction(fn)) {
    return fn;
  }
  try {
    const hasOwnWrapper = Object.prototype.hasOwnProperty.call(fn, "__sentry_wrapped__");
    if (hasOwnWrapper) {
      const wrapper = fn.__sentry_wrapped__;
      if (typeof wrapper === "function") {
        return wrapper;
      } else {
        return fn;
      }
    }
    if (core.getOriginalFunction(fn)) {
      return fn;
    }
  } catch {
    return fn;
  }
  const sentryWrapped = function(...args) {
    core.GLOBAL_OBJ._sentryWrappedDepth = (core.GLOBAL_OBJ._sentryWrappedDepth || 0) + 1;
    try {
      const wrappedArguments = args.map((arg) => wrap(arg, options));
      return fn.apply(this, wrappedArguments);
    } catch (ex) {
      ignoreNextOnError();
      core.withScope((scope) => {
        scope.addEventProcessor((event) => {
          if (options.mechanism) {
            core.addExceptionTypeValue(event, void 0, void 0);
            core.addExceptionMechanism(event, options.mechanism);
          }
          event.extra = {
            ...event.extra,
            arguments: args
          };
          return event;
        });
        core.captureException(ex);
      });
      throw ex;
    } finally {
      core.GLOBAL_OBJ._sentryWrappedDepth = (core.GLOBAL_OBJ._sentryWrappedDepth || 0) - 1;
    }
  };
  try {
    for (const property in fn) {
      if (Object.prototype.hasOwnProperty.call(fn, property)) {
        sentryWrapped[property] = fn[property];
      }
    }
  } catch {
  }
  core.markFunctionWrapped(sentryWrapped, fn);
  core.addNonEnumerableProperty(fn, "__sentry_wrapped__", sentryWrapped);
  try {
    const descriptor = Object.getOwnPropertyDescriptor(sentryWrapped, "name");
    if (descriptor.configurable) {
      Object.defineProperty(sentryWrapped, "name", {
        get() {
          return fn.name;
        }
      });
    }
  } catch {
  }
  return sentryWrapped;
}
function getHttpRequestData() {
  const url = browserUtils.getLocationHref();
  const { referrer } = WINDOW.document || {};
  const { userAgent } = WINDOW.navigator || {};
  const headers = {
    ...referrer && { Referer: referrer },
    ...userAgent && { "User-Agent": userAgent }
  };
  const request = {
    url,
    headers
  };
  return request;
}

exports.WINDOW = WINDOW;
exports.getHttpRequestData = getHttpRequestData;
exports.ignoreNextOnError = ignoreNextOnError;
exports.ignoreNextOnErrorMatching = ignoreNextOnErrorMatching;
exports.shouldIgnoreOnError = shouldIgnoreOnError;
exports.wrap = wrap;
//# sourceMappingURL=helpers.js.map
