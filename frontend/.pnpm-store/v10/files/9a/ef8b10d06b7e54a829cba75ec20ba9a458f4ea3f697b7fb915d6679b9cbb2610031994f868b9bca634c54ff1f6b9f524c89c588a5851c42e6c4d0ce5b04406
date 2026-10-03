interface InteractionsOptions {
    /**
     * The time that has to pass without any span being created.
     * If this time is exceeded, the interaction span will finish.
     *
     * Default: 1000 (ms)
     */
    idleTimeout?: number;
    /**
     * The max. time an interaction span may run.
     * If this time is exceeded, the interaction span will finish no matter what.
     *
     * Default: 30000 (ms)
     */
    finalTimeout?: number;
    /**
     * The max. time a child span of an interaction span may run.
     * If this time is exceeded, the interaction span will finish no matter what.
     *
     * Default: 15000 (ms)
     */
    childSpanTimeout?: number;
}
/**
 * Captures user interactions as spans.
 *
 * Important: This integration is considered experimental and might lead to noisy spans. Use at your own risk.
 *
 *
 * Clicks that happen outside of an in-progress pageload or navigation start an idle `ui.action.click` span,
 * named after the last known route, which collects everything the interaction triggers (requests, child spans,
 * …). Additionally, `ui.interaction.click` spans are recorded for the browser's own `event` timing entries.
 *
 * The integration requires `browserTracingIntegration` (or another source of pageload/navigation spans)
 * to know which route an interaction belongs to.
 *
 * @example
 * ```ts
 * Sentry.init({
 *   integrations: [Sentry.browserTracingIntegration(), Sentry.interactionsIntegration()],
 * });
 * ```
 */
export declare const interactionsIntegration: (options?: InteractionsOptions | undefined) => import("@sentry/core").Integration & {
    name: string;
};
export {};
//# sourceMappingURL=interactions.d.ts.map