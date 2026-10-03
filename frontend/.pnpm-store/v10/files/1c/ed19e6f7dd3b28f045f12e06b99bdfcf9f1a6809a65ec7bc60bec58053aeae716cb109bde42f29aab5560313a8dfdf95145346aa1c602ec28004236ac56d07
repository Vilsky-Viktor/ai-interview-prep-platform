Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const react = require('@sentry/react');
const appRouterRoutingInstrumentation = require('./appRouterRoutingInstrumentation.js');
const pagesRouterNavigationInstrumentation = require('./pagesRouterNavigationInstrumentation.js');
const pagesRouterRoutingInstrumentation = require('./pagesRouterRoutingInstrumentation.js');

function nextRouterInstrumentPageLoad(client) {
  const isAppRouter = !react.WINDOW.document.getElementById("__NEXT_DATA__");
  if (isAppRouter) {
    appRouterRoutingInstrumentation.appRouterInstrumentPageLoad(client);
  } else {
    pagesRouterRoutingInstrumentation.pagesRouterInstrumentPageLoad(client);
  }
}
function nextRouterInstrumentNavigation(client) {
  const isAppRouter = !react.WINDOW.document.getElementById("__NEXT_DATA__");
  if (isAppRouter) {
    appRouterRoutingInstrumentation.appRouterInstrumentNavigation(client);
  } else if (process.env._sentryHasPagesRouter !== "false") {
    pagesRouterNavigationInstrumentation.pagesRouterInstrumentNavigation(client);
  }
}

exports.nextRouterInstrumentNavigation = nextRouterInstrumentNavigation;
exports.nextRouterInstrumentPageLoad = nextRouterInstrumentPageLoad;
//# sourceMappingURL=nextRoutingInstrumentation.js.map
