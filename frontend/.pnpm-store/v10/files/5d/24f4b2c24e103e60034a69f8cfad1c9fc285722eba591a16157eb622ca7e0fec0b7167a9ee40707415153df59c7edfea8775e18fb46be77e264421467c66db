Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');

function setActiveSpanInBrowser(span) {
  const maybePreviousActiveSpan = core.getActiveSpan();
  if (maybePreviousActiveSpan === span) {
    return;
  }
  const scope = core.getCurrentScope();
  span.end = new Proxy(span.end, {
    apply(target, thisArg, args) {
      core._INTERNAL_setSpanForScope(scope, maybePreviousActiveSpan);
      return Reflect.apply(target, thisArg, args);
    }
  });
  core._INTERNAL_setSpanForScope(scope, span);
}

exports.setActiveSpanInBrowser = setActiveSpanInBrowser;
//# sourceMappingURL=setActiveSpan.js.map
