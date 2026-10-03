import type { Client, RequestHookInfo, ResponseHookInfo, Span, StartSpanOptions } from '@sentry/core';
import type { WebVitalsOptions } from '../integrations/webVitals';
export declare const BROWSER_TRACING_INTEGRATION_ID = "BrowserTracing";
/** Options for Browser Tracing integration */
export interface BrowserTracingOptions {
    /**
     * The time that has to pass without any span being created.
     * If this time is exceeded, the idle span will finish.
     *
     * Default: 1000 (ms)
     */
    idleTimeout: number;
    /**
     * The max. time an idle span may run.
     * If this time is exceeded, the idle span will finish no matter what.
     *
     * Default: 30000 (ms)
     */
    finalTimeout: number;
    /**
     The max. time an idle span may run.
     * If this time is exceeded, the idle span will finish no matter what.
     *
     * Default: 15000 (ms)
     */
    childSpanTimeout: number;
    /**
     * If a span should be created on page load.
     * If this is set to `false`, this integration will not start the default page load span.
     * Default: true
     */
    instrumentPageLoad: boolean;
    /**
     * If a span should be created on navigation (history change).
     * If this is set to `false`, this integration will not start the default navigation spans.
     * Default: true
     */
    instrumentNavigation: boolean;
    /**
     * If a navigation span should be created when the page is restored from the back/forward cache.
     *
     * This is deliberately independent of {@link BrowserTracingOptions.instrumentNavigation}: a restore
     * is not a history change, and the framework integrations that own their own navigation spans turn
     * that option off without ever handling a restore. The point of this span is trace hygiene, keeping
     * everything after the restore off the trace the page had before it was frozen, so it is worth
     * having even where history instrumentation is not.
     *
     * Default: true
     */
    instrumentBfcacheRestore: boolean;
    /**
     * Flag spans where tabs moved to background with "cancelled". Browser background tab timing is
     * not suited towards doing precise measurements of operations. By default, we recommend that this option
     * be enabled as background transactions can mess up your statistics in nondeterministic ways.
     *
     * Default: true
     */
    markBackgroundSpan: boolean;
    /**
     * If true, Sentry will capture long tasks and add them to the corresponding transaction.
     *
     * Default: true
     */
    enableLongTask: boolean;
    /**
     * If true, Sentry will capture long animation frames and add them to the corresponding transaction.
     *
     * Default: false
     */
    enableLongAnimationFrame: boolean;
    /**
     * If true, Sentry will capture first input delay and add it to the corresponding transaction.
     *
     * Default: true
     *
     * @deprecated Use {@link BrowserTracingOptions.webVitals} instead: `webVitals: { ignore: ['inp'] }`.
     */
    enableInp: boolean;
    /**
     * Options for the `webVitalsIntegration` that is auto-registered when none is present.
     * Ignored if you register `webVitalsIntegration` yourself.
     */
    webVitals?: WebVitalsOptions;
    /**
     * @deprecated This option is no longer used. Element timing is now tracked via the standalone
     * `elementTimingIntegration`. Add it to your `integrations` array to collect element timing metrics.
     */
    enableElementTiming?: boolean;
    /**
     * Flag to disable patching all together for fetch requests.
     *
     * Default: true
     */
    traceFetch: boolean;
    /**
     * Flag to disable patching all together for xhr requests.
     *
     * Default: true
     */
    traceXHR: boolean;
    /**
     * If true, Sentry will capture http timings and add them to the corresponding http spans.
     *
     * Default: true
     */
    enableHTTPTimings: boolean;
    /**
     * Resource spans with `op`s matching strings in the array will not be emitted.
     *
     * Default: []
     */
    ignoreResourceSpans: Array<'resource.script' | 'resource.css' | 'resource.img' | 'resource.other' | string>;
    /**
     * By default, the SDK will try to detect redirects and avoid creating separate spans for them.
     * If you want to opt-out of this behavior, you can set this option to `false`.
     *
     * Default: true
     */
    detectRedirects: boolean;
    /**
     * Link the currently started trace to a previous trace (e.g. a prior pageload, navigation or
     * manually started span). When enabled, this option will allow you to navigate between traces
     * in the Sentry UI.
     *
     * You can set this option to the following values:
     *
     * - `'in-memory'`: The previous trace data will be stored in memory.
     *   This is useful for single-page applications and enabled by default.
     *
     * - `'session-storage'`: The previous trace data will be stored in the `sessionStorage`.
     *   This is useful for multi-page applications or static sites but it means that the
     *   Sentry SDK writes to the browser's `sessionStorage`.
     *
     * - `'off'`: The previous trace data will not be stored or linked.
     *
     * You can also use {@link BrowserTracingOptions.consistentTraceSampling} to get
     * consistent trace sampling of subsequent traces. Otherwise, by default, your
     * `tracesSampleRate` or `tracesSampler` config significantly influences how often
     * traces will be linked.
     *
     * @default 'in-memory' - see explanation above
     */
    linkPreviousTrace: 'in-memory' | 'session-storage' | 'off';
    /**
     * If true, Sentry will consistently sample subsequent traces based on the
     * sampling decision of the initial trace. For example, if the initial page
     * load trace was sampled positively, all subsequent traces (e.g. navigations)
     * are also sampled positively. In case the initial trace was sampled negatively,
     * all subsequent traces are also sampled negatively.
     *
     * This option allows you to get consistent, linked traces within a user journey
     * while maintaining an overall quota based on your trace sampling settings.
     *
     * This option is only effective if {@link BrowserTracingOptions.linkPreviousTrace}
     * is enabled (i.e. not set to `'off'`).
     *
     * @default `false` - this is an opt-in feature.
     */
    consistentTraceSampling: boolean;
    /**
     * If set to `true`, the pageload span will not end itself automatically, unless it
     * runs until the {@link BrowserTracingOptions.finalTimeout} (30 seconds by default) is reached.
     *
     * Set this option to `true`, if you want full control over the pageload span duration.
     * You can use `Sentry.reportPageLoaded()` to manually end the pageload span whenever convenient.
     * Be aware that you have to ensure that this is always called, regardless of the chosen route
     * or path in the application.
     *
     * @default `false`. By default, the pageload span will end itself automatically, based on
     * the {@link BrowserTracingOptions.finalTimeout}, {@link BrowserTracingOptions.idleTimeout}
     * and {@link BrowserTracingOptions.childSpanTimeout}. This is more convenient to use but means
     * that the pageload duration can be arbitrary and might not be fully representative of a perceived
     * page load time.
     */
    enableReportPageLoaded: boolean;
    /**
     * A callback which is called before a span for a pageload or navigation is started.
     * It receives the options passed to `startSpan`, and expects to return an updated options object.
     */
    beforeStartSpan?: (options: StartSpanOptions) => StartSpanOptions;
    /**
     * This function will be called before creating a span for a request with the given url.
     * Return false if you don't want a span for the given url.
     *
     * Default: (url: string) => true
     */
    shouldCreateSpanForRequest?(this: void, url: string): boolean;
    /**
     * This callback is invoked directly after a span is started for an outgoing fetch or XHR request.
     * You can use it to annotate the span with additional data or attributes, for example by setting
     * attributes based on the passed request headers.
     */
    onRequestSpanStart?(span: Span, requestInformation: RequestHookInfo): void;
    /**
     * Is called when spans end for outgoing requests, providing access to response headers.
     */
    onRequestSpanEnd?(span: Span, responseInformation: ResponseHookInfo): void;
}
/**
 * The Browser Tracing integration automatically instruments browser pageload/navigation
 * actions as transactions, and captures requests, metrics and errors as spans.
 *
 * The integration can be configured with a variety of options, and can be extended to use
 * any routing library.
 *
 * We explicitly export the proper type here, as this has to be extended in some cases.
 */
export declare const browserTracingIntegration: (options?: Partial<BrowserTracingOptions>) => {
    name: string;
    setup(client: Client<import("@sentry/core").ClientOptions<import("@sentry/core").BaseTransportOptions>>): void;
    afterAllSetup(client: Client<import("@sentry/core").ClientOptions<import("@sentry/core").BaseTransportOptions>>): void;
};
/**
 * Manually start a page load span.
 * This will only do something if a browser tracing integration integration has been setup.
 *
 * If you provide a custom `traceOptions` object, it will be used to continue the trace
 * instead of the default behavior, which is to look it up on the <meta> tags.
 */
export declare function startBrowserTracingPageLoadSpan(client: Client, spanOptions: StartSpanOptions, traceOptions?: {
    sentryTrace?: string | undefined;
    baggage?: string | undefined;
}): Span | undefined;
/**
 * Manually start a navigation span.
 * This will only do something if a browser tracing integration has been setup.
 */
export declare function startBrowserTracingNavigationSpan(client: Client, spanOptions: StartSpanOptions, options?: {
    url?: string;
    isRedirect?: boolean;
}): Span | undefined;
/** Returns the value of a meta tag */
export declare function getMetaContent(metaName: string): string | undefined;
/** Returns the description of a server timing entry */
export declare function getServerTiming(name: string): string | undefined;
//# sourceMappingURL=browserTracingIntegration.d.ts.map