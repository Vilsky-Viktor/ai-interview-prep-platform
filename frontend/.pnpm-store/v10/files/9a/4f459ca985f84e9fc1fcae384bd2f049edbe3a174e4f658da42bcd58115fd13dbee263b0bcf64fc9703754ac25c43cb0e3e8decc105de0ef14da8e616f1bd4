import type { Span } from '@sentry/core';
interface UserTimingOptions {
    /**
     * User Timing entries with names matching any of these strings or regular expressions will not be emitted.
     *
     * Default: []
     */
    ignore?: Array<string | RegExp>;
}
/**
 * Captures spans created with the browser's User Timing APIs, `performance.mark` and `performance.measure`.
 *
 * The integration must be explicitly added to `Sentry.init`. Entries are attached to the active pageload or
 * navigation span when it ends.
 *
 * @example
 * ```ts
 * Sentry.init({
 *   integrations: [
 *     Sentry.browserTracingIntegration(),
 *     Sentry.userTimingIntegration({
 *       ignore: ['third-party-mark', /framework-measure/],
 *     }),
 *   ],
 * });
 * ```
 */
export declare const userTimingIntegration: (options?: UserTimingOptions | undefined) => import("@sentry/core").Integration & {
    name: string;
};
/**
 * Creates a span for a browser User Timing entry.
 * Exported only for tests.
 */
export declare function _addUserTimingSpan(parentSpan: Span, entry: PerformanceEntry, startTime: number, duration: number, timeOrigin: number, requestTime: number, ignore: Array<string | RegExp>): void;
export {};
//# sourceMappingURL=userTiming.d.ts.map