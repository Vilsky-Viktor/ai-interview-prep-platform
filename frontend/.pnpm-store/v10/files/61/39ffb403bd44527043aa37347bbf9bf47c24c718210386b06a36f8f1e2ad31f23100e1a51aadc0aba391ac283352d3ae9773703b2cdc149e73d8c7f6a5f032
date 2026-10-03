import { WINDOW } from '@sentry/react';
import { appRouterInstrumentNavigation, appRouterInstrumentPageLoad } from './appRouterRoutingInstrumentation.js';
import { pagesRouterInstrumentNavigation } from './pagesRouterNavigationInstrumentation.js';
import { pagesRouterInstrumentPageLoad } from './pagesRouterRoutingInstrumentation.js';

function nextRouterInstrumentPageLoad(client) {
  const isAppRouter = !WINDOW.document.getElementById("__NEXT_DATA__");
  if (isAppRouter) {
    appRouterInstrumentPageLoad(client);
  } else {
    pagesRouterInstrumentPageLoad(client);
  }
}
function nextRouterInstrumentNavigation(client) {
  const isAppRouter = !WINDOW.document.getElementById("__NEXT_DATA__");
  if (isAppRouter) {
    appRouterInstrumentNavigation(client);
  } else if (process.env._sentryHasPagesRouter !== "false") {
    pagesRouterInstrumentNavigation(client);
  }
}

export { nextRouterInstrumentNavigation, nextRouterInstrumentPageLoad };
//# sourceMappingURL=nextRoutingInstrumentation.js.map
