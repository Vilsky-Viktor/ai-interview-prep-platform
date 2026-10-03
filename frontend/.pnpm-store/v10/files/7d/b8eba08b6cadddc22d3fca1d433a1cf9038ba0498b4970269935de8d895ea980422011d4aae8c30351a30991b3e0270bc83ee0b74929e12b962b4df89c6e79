Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const utils = require('./utils.js');

function listenForWebVitalReportEvents(client, collectorCallback) {
  let pageloadSpan;
  let collected = false;
  function _runCollectorCallbackOnce() {
    if (!collected && pageloadSpan) {
      collectorCallback(pageloadSpan);
    }
    collected = true;
  }
  utils.onHidden(() => {
    _runCollectorCallbackOnce();
  });
  const unsubscribeStartNavigation = client.on("beforeStartNavigationSpan", (_, options) => {
    if (!options?.isRedirect) {
      _runCollectorCallbackOnce();
      unsubscribeStartNavigation();
      unsubscribeAfterStartPageLoadSpan();
    }
  });
  const unsubscribeAfterStartPageLoadSpan = client.on("afterStartPageLoadSpan", (span) => {
    pageloadSpan = span;
    unsubscribeAfterStartPageLoadSpan();
  });
}

exports.listenForWebVitalReportEvents = listenForWebVitalReportEvents;
//# sourceMappingURL=reportEvents.js.map
