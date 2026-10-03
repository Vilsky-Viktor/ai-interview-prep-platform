type InstrumentHandlerTypePerformanceObserver = 'longtask' | 'event' | 'navigation' | 'paint' | 'resource' | 'element' | 'soft-navigation' | 'first-input';
interface PerformanceEntry {
    readonly duration: number;
    readonly entryType: string;
    readonly name: string;
    readonly startTime: number;
    toJSON(): Record<string, unknown>;
}
export interface PerformanceEventTiming extends PerformanceEntry {
    processingStart: number;
    processingEnd: number;
    duration: number;
    cancelable?: boolean;
    target?: unknown | null;
    interactionId?: number;
}
/**
 * A `soft-navigation` entry, minted by the browser once a history change is followed by a
 * confirming paint. `interactionId` is the id of the `PerformanceEventTiming` entry for the
 * interaction that drove the navigation, which is how we join it back to a Sentry navigation span.
 */
export interface PerformanceSoftNavigation extends PerformanceEntry {
    readonly interactionId: number;
    readonly navigationId: number;
}
interface PerformanceScriptTiming extends PerformanceEntry {
    sourceURL: string;
    sourceFunctionName: string;
    sourceCharPosition: number;
    invoker: string;
    invokerType: string;
}
export interface PerformanceLongAnimationFrameTiming extends PerformanceEntry {
    scripts: PerformanceScriptTiming[];
}
/**
 * The navigation types web-vitals reports a metric for, reported as-is on `browser.navigation.type`.
 */
export type MetricNavigationType = 'navigate' | 'reload' | 'back-forward' | 'back-forward-cache' | 'prerender' | 'restore' | 'soft-navigation';
interface Metric {
    /**
     * The name of the metric (in acronym form).
     */
    name: 'CLS' | 'FCP' | 'INP' | 'LCP' | 'TTFB';
    /**
     * The current value of the metric.
     */
    value: number;
    /**
     * The rating as to whether the metric value is within the "good",
     * "needs improvement", or "poor" thresholds of the metric.
     */
    rating: 'good' | 'needs-improvement' | 'poor';
    /**
     * The delta between the current value and the last-reported value.
     * On the first report, `delta` and `value` will always be the same.
     */
    delta: number;
    /**
     * A unique ID representing this particular metric instance. This ID can
     * be used by an analytics tool to dedupe multiple values sent for the same
     * metric instance, or to group multiple deltas together and calculate a
     * total. It can also be used to differentiate multiple different metric
     * instances sent from the same page, which can happen if the page is
     * restored from the back/forward cache (in that case new metrics object
     * get created).
     */
    id: string;
    /**
     * Any performance entries relevant to the metric value calculation.
     * The array may also be empty if the metric value was not based on any
     * entries (e.g. a CLS value of 0 given no layout shifts).
     */
    entries: PerformanceEntry[];
    /**
     * The type of navigation.
     *
     * Navigation Timing API (or `undefined` if the browser doesn't
     * support that API). For pages that are restored from the bfcache, this
     * value will be 'back-forward-cache'.
     */
    navigationType: MetricNavigationType;
    /**
     * The id of the navigation the metric belongs to. For soft navigations this is the
     * `navigationId` of the `soft-navigation` entry, otherwise it's the id of the hard navigation.
     */
    navigationId: number;
    /**
     * For soft navigations, the `interactionId` of the interaction that triggered the navigation.
     */
    navigationInteractionId?: number;
    /**
     * The start time the metric value is relative to. Non-zero for soft navigations, where the
     * time origin is the triggering interaction rather than the start of the document.
     */
    navigationStartTime?: number;
    /**
     * The URL the metric was recorded for. Relevant for soft navigations, where a metric can be
     * reported long after the URL has moved on.
     */
    navigationURL?: string;
}
type CleanupHandlerCallback = () => void;
/**
 * Opt the CLS, LCP and INP observers into reporting metrics for soft navigations.
 *
 * This also turns `reportAllChanges` off for CLS and LCP. web-vitals force-reports a metric when
 * the navigation it belongs to is over, so without the intermediate updates every value a handler
 * receives is already the final one for its navigation. That only holds because soft navigations
 * are limited to span streaming, where CLS and LCP are sent as their own spans - the static
 * lifecycle instead writes them onto the pageload span as it ends, which is what `reportAllChanges`
 * was originally added for (#11934, #12360).
 *
 * Each observer is instrumented lazily, on its first handler, and web-vitals takes its options at
 * that point only. So this has to be called before any of the `add*InstrumentationHandler`
 * functions, otherwise it won't take effect for observers that are already running.
 *
 * On browsers without the Soft Navigation API this is a no-op: web-vitals feature-detects the API
 * and keeps reporting hard-navigation metrics as usual.
 */
export declare function enableSoftNavigationReporting(): void;
/**
 * Opt the CLS, LCP and INP observers into reporting metrics for back/forward-cache restores.
 *
 * web-vitals re-reports each metric after a restore, tagged with a `back-forward-cache` navigation
 * type. A restore is a new page view measured against a document that was never reloaded, so the
 * values only mean anything if there is a fresh root span for them to belong to. Without one they
 * would attach to the span the page had before it was frozen, which is why this is off by default.
 *
 * Like `enableSoftNavigationReporting`, this only affects observers instrumented after it is
 * called.
 */
export declare function enableBfcacheReporting(): void;
/**
 * Add a callback that will be triggered when a CLS metric is available.
 * Returns a cleanup callback which can be called to remove the instrumentation handler.
 *
 * Pass `stopOnCallback = true` to stop listening for CLS when the cleanup callback is called.
 * This will lead to the CLS being finalized and frozen.
 */
export declare function addClsInstrumentationHandler(callback: (data: {
    metric: Metric;
}) => void, stopOnCallback?: boolean): CleanupHandlerCallback;
/**
 * Add a callback that will be triggered when a LCP metric is available.
 * Returns a cleanup callback which can be called to remove the instrumentation handler.
 *
 * Pass `stopOnCallback = true` to stop listening for LCP when the cleanup callback is called.
 * This will lead to the LCP being finalized and frozen.
 */
export declare function addLcpInstrumentationHandler(callback: (data: {
    metric: Metric;
}) => void, stopOnCallback?: boolean): CleanupHandlerCallback;
/**
 * Add a callback that will be triggered when a TTFD metric is available.
 */
export declare function addTtfbInstrumentationHandler(callback: (data: {
    metric: Metric;
}) => void): CleanupHandlerCallback;
/**
 * Add a callback that will be triggered when a FCP metric is available.
 */
export declare function addFcpInstrumentationHandler(callback: (data: {
    metric: Metric;
}) => void): CleanupHandlerCallback;
export type InstrumentationHandlerCallback = (data: {
    metric: Omit<Metric, 'entries'> & {
        entries: PerformanceEventTiming[];
    };
}) => void;
/**
 * Add a callback that will be triggered when a INP metric is available.
 * Returns a cleanup callback which can be called to remove the instrumentation handler.
 */
export declare function addInpInstrumentationHandler(callback: InstrumentationHandlerCallback): CleanupHandlerCallback;
export declare function addPerformanceInstrumentationHandler(type: 'event', callback: (data: {
    entries: ((PerformanceEntry & {
        target?: unknown | null;
    }) | PerformanceEventTiming)[];
}) => void): CleanupHandlerCallback;
export declare function addPerformanceInstrumentationHandler(type: InstrumentHandlerTypePerformanceObserver, callback: (data: {
    entries: PerformanceEntry[];
}) => void): CleanupHandlerCallback;
/**
 * Check if a PerformanceEntry is a PerformanceEventTiming by checking for the `duration` property.
 */
export declare function isPerformanceEventTiming(entry: PerformanceEntry): entry is PerformanceEventTiming;
export {};
//# sourceMappingURL=performanceObserver.d.ts.map