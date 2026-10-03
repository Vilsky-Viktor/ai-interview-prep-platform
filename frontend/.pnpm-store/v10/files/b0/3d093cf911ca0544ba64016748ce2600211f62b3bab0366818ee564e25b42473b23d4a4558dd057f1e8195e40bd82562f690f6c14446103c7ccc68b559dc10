export declare const WEB_VITALS_INTEGRATION_NAME: 'WebVitals';
export type WebVitalName = 'cls' | 'inp' | 'lcp';
export interface WebVitalsOptions {
    /**
     * Web vitals to skip.
     */
    ignore?: WebVitalName[];
    /**
     * Give each soft navigation its own set of LCP, CLS and INP, detected through the browser's
     * [Soft Navigations API](https://developer.chrome.com/docs/web-platform/soft-navigations-experiment)
     * (Chromium 151+).
     *
     * Each soft navigation's vitals are reported against the navigation span they belong to. This
     * also changes how the initial page load is measured: its vitals are finalized at the first soft
     * navigation rather than accumulating over the page's lifetime.
     *
     * Soft navigations the browser doesn't detect (programmatic navigations, navigations that never
     * paint) report no vitals at all, so coverage is lower than for page loads. Set this to `false`
     * to report a single set of vitals for the whole page lifetime instead.
     *
     * Requires span streaming (`traceLifecycle: 'stream'`, the default), since soft navigation vitals
     * are finalized long after the navigation span they belong to has ended. Ignored in browsers
     * without support for the Soft Navigations API.
     *
     * Default: `true`
     */
    softNavigations?: boolean;
    /**
     * Give each back/forward-cache restore its own set of LCP, CLS and INP.
     *
     * A restore is a new page view measured against a document that was never reloaded, so its vitals
     * are reported against the navigation span `browserTracingIntegration` starts for the restore,
     * and tagged `browser.navigation.type: back-forward-cache`. A restore is near-instant by construction, so
     * these are a distinct population from page load vitals and are meant to be read through that
     * attribute rather than pooled with them. Set this to `false` to leave restores unmeasured.
     *
     * Requires span streaming (`traceLifecycle: 'stream'`, the default) and
     * `browserTracingIntegration`, which supplies the navigation span these attach to.
     *
     * Default: `true`
     */
    bfcacheNavigations?: boolean;
}
/**
 * Captures Core Web Vitals (LCP, CLS, INP) and related pageload vitals.
 *
 * `browserTracingIntegration` auto-registers this integration if no
 * `webVitalsIntegration` is already present, so explicit registration is only
 * needed to customize options or to use it without `browserTracingIntegration`.
 */
export declare const webVitalsIntegration: (options?: WebVitalsOptions | undefined) => import("@sentry/core").Integration & {
    name: "WebVitals";
};
//# sourceMappingURL=webVitals.d.ts.map