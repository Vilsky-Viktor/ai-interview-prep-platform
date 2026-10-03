import type { Span, SpanAttributes } from '@sentry/core';
import type { MetricNavigationType } from '../instrumentation/performanceObserver';
export interface LayoutShift extends PerformanceEntry {
    value: number;
    sources: Array<{
        node: Node | null;
    }>;
    hadRecentInput: boolean;
}
export interface LargestContentfulPaint extends PerformanceEntry {
    readonly renderTime: DOMHighResTimeStamp;
    readonly loadTime: DOMHighResTimeStamp;
    readonly size: number;
    readonly id: string;
    readonly url: string;
    readonly element: Element | null;
}
interface WebVitalSpanOptions {
    name: string;
    op: string;
    origin: string;
    metricName: 'lcp' | 'cls' | 'inp';
    value: number;
    attributes?: SpanAttributes;
    parentSpan?: Span;
    startTime: number;
    endTime?: number;
    /** Set when the vital was reported for a soft navigation rather than the initial page load. */
    softNavigationId?: number;
    /** The navigation the vital was measured on, as reported by web-vitals. */
    navigationType?: MetricNavigationType;
    /**
     * When `true`, the span is sent on its own as a v2 streamed span instead of being folded into a
     * transaction. Used for INP when span streaming is disabled (it reports late, so it can't ride
     * the pageload transaction).
     *
     * TODO(standalone): remove once the static (transaction) trace lifecycle is dropped and INP always streams.
     */
    standalone?: boolean;
}
/**
 * Emits a web vital span. When `standalone` is set it is sent on its own as a v2 streamed span;
 * otherwise it flows through the span streaming pipeline as a child of `parentSpan`.
 */
export declare function _emitWebVitalSpan(options: WebVitalSpanOptions): void;
export {};
//# sourceMappingURL=emitSpan.d.ts.map