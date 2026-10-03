import type { Client, Span } from '@sentry/core';
import type { InstrumentationHandlerCallback, MetricNavigationType } from '../instrumentation/performanceObserver';
import type { LargestContentfulPaint, LayoutShift } from './emitSpan';
import type { PerformanceEventTiming } from '../instrumentation/performanceObserver';
type InpMetric = Parameters<InstrumentationHandlerCallback>[0]['metric'];
/**
 * Tracks LCP as a streamed span.
 */
export declare function trackLcpAsSpan(client: Client, perNavigation?: boolean): void;
/**
 * Exported only for testing.
 */
export declare function _sendLcpSpan(lcpValue: number, entry: LargestContentfulPaint | undefined, pageloadSpan?: Span, softNavigationId?: number, navigationType?: MetricNavigationType, navigationStartTime?: number): void;
/**
 * Tracks CLS as a streamed span.
 */
export declare function trackClsAsSpan(client: Client, perNavigation?: boolean): void;
/**
 * Exported only for testing.
 */
export declare function _sendClsSpan(clsValue: number, entry: LayoutShift | undefined, pageloadSpan?: Span, softNavigationId?: number, navigationType?: MetricNavigationType, navigationStartTime?: number): void;
/**
 * Tracks INP and emits it as a web vital span, as a child of the interaction's root span.
 * Requires `registerInpInteractionListener()` to be called separately for cached element names and
 * root spans per interaction.
 */
export declare function trackInpAsSpan(client: Client, perNavigation?: boolean): void;
/**
 * Exported only for testing.
 */
export declare function _sendInpSpan(inpValue: number, entry: PerformanceEventTiming | undefined, standalone?: boolean, attributedSpan?: Span, softNavigationId?: number, metric?: InpMetric): void;
export {};
//# sourceMappingURL=spans.d.ts.map