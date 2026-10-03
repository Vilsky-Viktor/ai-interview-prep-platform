import type { Span, SpanAttributes } from '@sentry/core';
/**
 * Start tracking long tasks.
 */
export declare function startTrackingLongTasks(): void;
/**
 * Start tracking long animation frames.
 */
export declare function startTrackingLongAnimationFrames(): void;
interface AddPerformanceEntriesOptions {
    /**
     * Resource spans with `op`s matching strings in the array will not be emitted.
     *
     * Default: []
     */
    ignoreResourceSpans: Array<'resource.script' | 'resource.css' | 'resource.img' | 'resource.other' | string>;
    /**
     * Whether span streaming is enabled.
     */
    spanStreamingEnabled?: boolean;
}
/** Add performance related spans to a transaction */
export declare function addPerformanceEntries(span: Span, options: AddPerformanceEntriesOptions): void;
/**
 * Create a span for a browser paint performance entry.
 * Exported only for tests.
 */
export declare function _addPaintSpan(span: Span, entry: PerformanceEntry, startTime: number, duration: number, timeOrigin: number): void;
/**
 * Instrument navigation entries
 * exported only for tests
 */
export declare function _addNavigationSpans(span: Span, entry: PerformanceNavigationTiming, timeOrigin: number, spanStreamingEnabled?: boolean): void;
/**
 * Create resource-related spans.
 * Exported only for tests.
 */
export declare function _addResourceSpans(span: Span, entry: PerformanceResourceTiming, resourceUrl: string, startTime: number, duration: number, timeOrigin: number, ignoredResourceSpanOps?: Array<string>, spanStreamingEnabled?: boolean): void;
type ExperimentalResourceTimingProperty = 'renderBlockingStatus' | 'deliveryType' | 'responseStatus';
/**
 * Use this to set any attributes we can take directly form the PerformanceResourceTiming entry.
 *
 * This is just a mapping function for entry->attribute to keep bundle-size minimal.
 * Experimental properties are also accepted (see {@link ExperimentalResourceTimingProperty}).
 * Assumes that all entry properties might be undefined for browser-specific differences.
 * Only accepts string and number values for now and also sets 0-values.
 */
export declare function _setResourceRequestAttributes(entry: Partial<PerformanceResourceTiming> & Partial<Record<ExperimentalResourceTimingProperty, number | string>>, attributes: SpanAttributes, properties: [keyof PerformanceResourceTiming | ExperimentalResourceTimingProperty, string][]): void;
export {};
//# sourceMappingURL=entries.d.ts.map