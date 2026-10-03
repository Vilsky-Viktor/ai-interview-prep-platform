import { onHidden } from './utils.js';

function listenForWebVitalReportEvents(client, collectorCallback) {
  let pageloadSpan;
  let collected = false;
  function _runCollectorCallbackOnce() {
    if (!collected && pageloadSpan) {
      collectorCallback(pageloadSpan);
    }
    collected = true;
  }
  onHidden(() => {
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

export { listenForWebVitalReportEvents };
//# sourceMappingURL=reportEvents.js.map
