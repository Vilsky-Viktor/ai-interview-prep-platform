Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const browser = require('@sentry/core/browser');
const attributes = require('@sentry/conventions/attributes');
const types = require('../types.js');

function _emitWebVitalSpan(options) {
  const {
    name,
    op,
    origin,
    metricName,
    value,
    attributes: passedAttributes,
    parentSpan,
    startTime,
    endTime,
    standalone,
    softNavigationId,
    navigationType
  } = options;
  const segmentSpan = parentSpan && core.getRootSpan(parentSpan);
  const segmentName = segmentSpan ? core.spanToJSON(segmentSpan).name : core.getCurrentScope().getScopeData().transactionName;
  const attributes$1 = {
    [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: origin,
    [core.SEMANTIC_ATTRIBUTE_SENTRY_OP]: op,
    [core.SEMANTIC_ATTRIBUTE_EXCLUSIVE_TIME]: 0,
    [`browser.web_vital.${metricName}.value`]: value,
    // oxlint-disable-next-line typescript-eslint/no-deprecated
    [attributes.SENTRY_TRANSACTION]: segmentName,
    [attributes.SENTRY_SEGMENT_NAME]: segmentName,
    // Web vital score calculation relies on the user agent
    [attributes.USER_AGENT_ORIGINAL]: types.WINDOW.navigator?.userAgent,
    ...passedAttributes
  };
  if (parentSpan && core.spanToJSON(parentSpan).attributes[core.SEMANTIC_ATTRIBUTE_SENTRY_OP] === "pageload") {
    attributes$1["sentry.pageload.span_id"] = parentSpan.spanContext().spanId;
  }
  if (softNavigationId != null) {
    attributes$1[attributes.BROWSER_NAVIGATION_ID] = softNavigationId;
  }
  if (navigationType) {
    attributes$1[attributes.BROWSER_NAVIGATION_TYPE] = navigationType;
  }
  if (standalone) {
    Object.assign(attributes$1, getReplayAttributes());
  }
  const span = browser.startInactiveSpan({
    name,
    attributes: attributes$1,
    startTime,
    parentSpan,
    // oxlint-disable-next-line typescript/no-deprecated -- intentional during the v1/v2 transition; see the TODO(standalone) above
    experimental: standalone ? { standalone: true } : void 0
  });
  if (span) {
    span.end(endTime ?? startTime);
  }
}
function getReplayAttributes() {
  const replay = core.getClient()?.getIntegrationByName("Replay");
  const replayId = replay?.getReplayId(true);
  if (!replayId) {
    return {};
  }
  return {
    [attributes.SENTRY_REPLAY_ID]: replayId,
    // Not the `SENTRY_REPLAY_IS_BUFFERING` convention: that one has no `sentry._internal.` prefix, and
    // the rest of the SDK sets the prefixed key (see `logs/internal.ts`, `metrics/internal.ts`).
    "sentry._internal.replay_is_buffering": replay.getRecordingMode() === "buffer" ? true : void 0
  };
}

exports._emitWebVitalSpan = _emitWebVitalSpan;
//# sourceMappingURL=emitSpan.js.map
