import type { Span, SpanTimeInput, StartSpanOptions } from '@sentry/core';
/**
 * Checks if a given value is a valid measurement value.
 */
export declare function isMeasurementValue(value: unknown): value is number;
/**
 * Helper function to start child on transactions. This function will make sure that the transaction will
 * use the start timestamp of the created child span if it is earlier than the transactions actual
 * start timestamp.
 */
export declare function startAndEndSpan(parentSpan: Span, startTimeInSeconds: number, endTime: SpanTimeInput, { ...ctx }: StartSpanOptions): Span | undefined;
/** Get the browser performance API. */
export declare function getBrowserPerformanceAPI(): Performance | undefined;
/**
 * Converts from milliseconds to seconds
 * @param time time in ms
 */
export declare function msToSec(time: number): number;
/**
 * Converts ALPN protocol ids to name and version.
 *
 * (https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml#alpn-protocol-ids)
 * @param nextHopProtocol PerformanceResourceTiming.nextHopProtocol
 */
export declare function extractNetworkProtocol(nextHopProtocol: string): {
    name: string;
    version: string;
};
/**
 * Generic support check for web vitals
 */
export declare function supportsWebVital(entryType: 'layout-shift' | 'largest-contentful-paint'): boolean;
//# sourceMappingURL=utils.d.ts.map