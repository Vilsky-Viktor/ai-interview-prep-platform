import { LRUMap, spanToJSON, SEMANTIC_ATTRIBUTE_SENTRY_OP, debug } from '@sentry/core';
import { BROWSER_NAVIGATION_ID } from '@sentry/conventions/attributes';
import { DEBUG_BUILD } from '../debug-build.js';
import { addPerformanceInstrumentationHandler, isPerformanceEventTiming } from '../instrumentation/performanceObserver.js';
import { WINDOW } from '../types.js';

const MAX_TRACKED_NAVIGATIONS = 5;
const INTERACTION_MATCH_TOLERANCE_MS = 5;
let _pendingNavigation;
let _pendingInteraction;
let _lastInteractionTimestamp;
const _interactionIdToNavigationSpan = new LRUMap(MAX_TRACKED_NAVIGATIONS);
const _navigationIdToNavigationSpan = new LRUMap(MAX_TRACKED_NAVIGATIONS);
let _correlationStarted = false;
function interactionMatches(entryStartTime, interactionTimestamp) {
  return Math.abs(entryStartTime - interactionTimestamp) <= INTERACTION_MATCH_TOLERANCE_MS;
}
function supportsSoftNavigations() {
  try {
    return PerformanceObserver.supportedEntryTypes.includes("soft-navigation") && // Older implementations exposed this as an attribute rather than a method. Only the method
    // form shipped unflagged, so it's what web-vitals gates on.
    typeof WINDOW.PerformanceSoftNavigation?.prototype?.getLargestInteractionContentfulPaint === "function";
  } catch {
    return false;
  }
}
function startSoftNavigationCorrelation(client) {
  if (_correlationStarted || !supportsSoftNavigations()) {
    return;
  }
  _correlationStarted = true;
  const onInteraction = (event) => {
    if (event.isTrusted) {
      _lastInteractionTimestamp = event.timeStamp;
    }
  };
  WINDOW.addEventListener("click", onInteraction, { capture: true, passive: true });
  WINDOW.addEventListener("keydown", onInteraction, { capture: true, passive: true });
  client.on("spanStart", (span) => {
    if (spanToJSON(span).attributes?.[SEMANTIC_ATTRIBUTE_SENTRY_OP] !== "navigation") {
      return;
    }
    _pendingNavigation = void 0;
    const interactionTimestamp = _lastInteractionTimestamp;
    if (interactionTimestamp == null) {
      return;
    }
    if (_pendingInteraction?.interactionTimestamp === interactionTimestamp) {
      _interactionIdToNavigationSpan.set(_pendingInteraction.interactionId, span);
      _pendingInteraction = void 0;
      return;
    }
    _pendingNavigation = { span, interactionTimestamp };
  });
  const bindInteractionToNavigationSpan = ({ entries }) => {
    for (const entry of entries) {
      if (!isPerformanceEventTiming(entry) || !entry.interactionId) {
        continue;
      }
      const pending = _pendingNavigation;
      if (pending && interactionMatches(entry.startTime, pending.interactionTimestamp)) {
        _interactionIdToNavigationSpan.set(entry.interactionId, pending.span);
        _pendingNavigation = void 0;
        continue;
      }
      if (_interactionIdToNavigationSpan.get(entry.interactionId)) {
        continue;
      }
      if (_lastInteractionTimestamp != null && interactionMatches(entry.startTime, _lastInteractionTimestamp)) {
        _pendingInteraction = { interactionId: entry.interactionId, interactionTimestamp: _lastInteractionTimestamp };
      }
    }
  };
  addPerformanceInstrumentationHandler("event", bindInteractionToNavigationSpan);
  addPerformanceInstrumentationHandler("first-input", bindInteractionToNavigationSpan);
  addPerformanceInstrumentationHandler("soft-navigation", ({ entries }) => {
    for (const entry of entries) {
      const span = _interactionIdToNavigationSpan.get(entry.interactionId);
      if (!span) {
        DEBUG_BUILD && debug.log(`[SoftNav] No navigation span found for soft navigation ${entry.navigationId}`, entry);
        continue;
      }
      _navigationIdToNavigationSpan.set(entry.navigationId, span);
      span.setAttribute(BROWSER_NAVIGATION_ID, entry.navigationId);
    }
  });
}
function getNavigationSpanForMetric(metric) {
  if (metric.navigationType !== "soft-navigation") {
    return void 0;
  }
  const span = _navigationIdToNavigationSpan.get(metric.navigationId);
  if (span) {
    return span;
  }
  return metric.navigationInteractionId != null ? _interactionIdToNavigationSpan.get(metric.navigationInteractionId) : void 0;
}

export { getNavigationSpanForMetric, startSoftNavigationCorrelation, supportsSoftNavigations };
//# sourceMappingURL=softNavs.js.map
