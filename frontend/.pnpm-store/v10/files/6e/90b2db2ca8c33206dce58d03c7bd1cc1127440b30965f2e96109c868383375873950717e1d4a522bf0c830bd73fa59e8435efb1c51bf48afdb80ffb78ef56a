import type { Client, Span } from '@sentry/core';
interface StartTrackingWebVitalsOptions {
    trackCls: boolean;
    trackLcp: boolean;
    client: Client;
}
/**
 * Start tracking web vitals.
 * The callback returned by this function can be used to stop tracking & ensure all measurements are final & captured.
 *
 * @returns A function that forces web vitals collection
 */
export declare function startTrackingWebVitals({ trackCls, trackLcp }: StartTrackingWebVitalsOptions): () => void;
export { registerInpInteractionListener } from './inp';
interface AddWebVitalsToSpanOptions {
    /**
     * Flag to determine if CLS should be recorded as a measurement on the pageload span or
     * sent as a standalone span instead.
     * Sending it as a standalone span will yield more accurate LCP values.
     *
     * Default: `false` for backwards compatibility.
     */
    recordClsOnPageloadSpan: boolean;
    /**
     * Flag to determine if LCP should be recorded as a measurement on the pageload span or
     * sent as a standalone span instead.
     * Sending it as a standalone span will yield more accurate LCP values.
     *
     * Default: `false` for backwards compatibility.
     */
    recordLcpOnPageloadSpan: boolean;
    /**
     * Whether span streaming is enabled.
     */
    spanStreamingEnabled?: boolean;
}
/**
 * Writes the collected web vitals (LCP, CLS, INP, TTFB, FP, FCP) onto the pageload span,
 * either as measurements/attributes (v1) or as web vital attributes (span streaming).
 *
 * This should be called when the pageload span ends, after the web vitals have been finalized.
 * It is a no-op for non-pageload spans, but always resets the collected web vital state so it
 * doesn't leak into a subsequent navigation.
 */
export declare function addWebVitalsToSpan(span: Span, options: AddWebVitalsToSpanOptions): void;
//# sourceMappingURL=tracking.d.ts.map