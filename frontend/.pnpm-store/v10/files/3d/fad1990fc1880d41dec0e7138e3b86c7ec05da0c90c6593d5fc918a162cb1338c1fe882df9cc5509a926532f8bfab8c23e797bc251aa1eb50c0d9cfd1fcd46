import type { Span, StartSpanOptions } from '@sentry/core';
/**
 * Next.js-specific implementation of `startSpan` that skips span creation
 * in Cache Components contexts (which render at build time).
 *
 * When in a Cache Components context, we execute the callback with a non-recording span
 * and return early without creating an actual span, since spans don't make sense at build/cache time.
 *
 * @param options - Options for starting the span
 * @param callback - Callback function that receives the span
 * @returns The return value of the callback
 */
export declare function startSpan<T>(options: StartSpanOptions, callback: (span: Span) => T): T;
/**
 *
 * When in a Cache Components context, we execute the callback with a non-recording span
 * and return early without creating an actual span, since spans don't make sense at build/cache time.
 *
 * @param options - Options for starting the span
 * @param callback - Callback function that receives the span and finish function
 * @returns The return value of the callback
 */
export declare function startSpanManual<T>(options: StartSpanOptions, callback: (span: Span, finish: () => void) => T): T;
/**
 *
 * When in a Cache Components context, we return a non-recording span and return early
 * without creating an actual span, since spans don't make sense at build/cache time.
 *
 * @param options - Options for starting the span
 * @returns A non-recording span (in Cache Components context) or the created span
 */
export declare function startInactiveSpan(options: StartSpanOptions): Span;
//# sourceMappingURL=nextSpan.d.ts.map