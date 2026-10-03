import type { Client, Span } from '@sentry/core';
interface SoftNavMetric {
    navigationType: string;
    navigationId: number;
    navigationInteractionId?: number;
}
/**
 * Whether the browser can report web vitals for soft navigations.
 *
 * This mirrors web-vitals' own feature detection: passing `reportSoftNavs` on a browser that fails
 * this check is a no-op there, so it has to be a no-op here too.
 */
export declare function supportsSoftNavigations(): boolean;
/**
 * Start correlating the browser's soft navigations with the SDK's navigation spans.
 *
 * A navigation span is created synchronously on the history change, but the browser only mints the
 * `soft-navigation` entry (and with it the `navigationId` that web vitals are reported against)
 * once the navigation has been confirmed by a paint. So the `navigationId` cannot be known at span
 * creation time and the two have to be joined after the fact.
 *
 * The join key is the `interactionId` of the interaction that drove the navigation: per the Soft
 * Navigations spec the `soft-navigation` entry carries the `interactionId` of the interaction that
 * triggered it, which is the same id the interaction's own `PerformanceEventTiming` entry carries.
 * So we bind a navigation span to the interaction it happened during, and the soft navigation
 * joins back to that span through the shared id.
 *
 * This is inherently partial. Navigations that don't meet the browser's soft navigation heuristic
 * (programmatic navigations, navigations that never paint, back/forward from the browser chrome)
 * produce no entry at all, so those navigation spans simply have no web vitals.
 */
export declare function startSoftNavigationCorrelation(client: Client): void;
/**
 * The navigation span a soft navigation web vital belongs to, or `undefined` if the metric isn't
 * for a soft navigation or we failed to correlate it.
 */
export declare function getNavigationSpanForMetric(metric: SoftNavMetric): Span | undefined;
export {};
//# sourceMappingURL=softNavs.d.ts.map