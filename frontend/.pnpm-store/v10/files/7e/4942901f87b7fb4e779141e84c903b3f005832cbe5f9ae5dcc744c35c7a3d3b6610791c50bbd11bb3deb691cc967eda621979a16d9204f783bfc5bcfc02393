import type { ClientOptions, Event, EventHint, Options as CoreOptions, ParameterizedString, Scope, SeverityLevel } from '@sentry/core';
import type { BrowserClientReplayOptions } from '@sentry/core/browser';
import { Client } from '@sentry/core';
import type { BrowserTransportOptions } from './transports/types';
export type BrowserClientProfilingOptions = {
    /**
     * Sets profiling session sample rate for the entire profiling session.
     *
     * A profiling session corresponds to a user session, meaning it is set once at integration initialization and
     * persisted until the next page reload. This rate determines what percentage of user sessions will have profiling enabled.
     * @default 0
     */
    profileSessionSampleRate?: number;
    /**
     * Set the lifecycle mode of the profiler.
     * - **manual**: The profiler will be manually started and stopped via `startProfiler`/`stopProfiler`.
     *    If a session is sampled, is dependent on the `profileSessionSampleRate`.
     * - **trace**: The profiler will be automatically started when a root span exists and stopped when there are no
     *    more sampled root spans. Whether a session is sampled, is dependent on the `profileSessionSampleRate` and the
     *    existing sampling configuration for tracing (`tracesSampleRate`/`tracesSampler`).
     *
     * @default 'manual'
     */
    profileLifecycle?: 'manual' | 'trace';
};
type BrowserSpecificOptions = BrowserClientReplayOptions & BrowserClientProfilingOptions & {
    /** If configured, this URL will be used as base URL for lazy loading integration. */
    cdnBaseUrl?: string;
    /**
     * Important: Only set this option if you know what you are doing!
     *
     * By default, the SDK will check if `Sentry.init` is called in a browser extension.
     * In case it is, it will stop initialization and log a warning
     * because browser extensions require a different Sentry initialization process:
     * https://docs.sentry.io/platforms/javascript/best-practices/shared-environments/
     *
     * Setting up the SDK in a browser extension with global error monitoring is not recommended
     * and will likely flood you with errors from other web sites or extensions. This can heavily
     * impact your quota and cause interference with your and other Sentry SDKs in shared environments.
     *
     * If this check wrongfully flags your setup as a browser extension, you can set this
     * option to `true` to skip the check.
     *
     * @default false
     */
    skipBrowserExtensionCheck?: boolean;
    /**
     * If you use Spotlight by Sentry during development, use
     * this option to forward captured Sentry events to Spotlight.
     *
     * Either set it to true, or provide a specific Spotlight Sidecar URL.
     *
     * More details: https://spotlightjs.com/
     *
     * IMPORTANT: Only set this option to `true` while developing, not in production!
     */
    spotlight?: boolean | string;
};
/**
 * Configuration options for the Sentry Browser SDK.
 * @see @sentry/core Options for more information.
 */
export type BrowserOptions = CoreOptions<BrowserTransportOptions> & BrowserSpecificOptions;
/**
 * Configuration options for the Sentry Browser SDK Client class
 * @see BrowserClient for more information.
 */
export type BrowserClientOptions = ClientOptions<BrowserTransportOptions> & BrowserSpecificOptions;
/**
 * The Sentry Browser SDK Client.
 *
 * @see BrowserOptions for documentation on configuration options.
 * @see SentryClient for usage documentation.
 */
export declare class BrowserClient extends Client<BrowserClientOptions> {
    /**
     * Creates a new Browser SDK instance.
     *
     * @param options Configuration options for this SDK.
     */
    constructor(options: BrowserClientOptions);
    /**
     * @inheritDoc
     */
    eventFromException(exception: unknown, hint?: EventHint): PromiseLike<Event>;
    /**
     * @inheritDoc
     */
    eventFromMessage(message: ParameterizedString, level?: SeverityLevel, hint?: EventHint): PromiseLike<Event>;
    /**
     * @inheritDoc
     */
    protected _prepareEvent(event: Event, hint: EventHint, currentScope: Scope, isolationScope: Scope): PromiseLike<Event | null>;
}
/** Exported only for tests. */
export declare function applyDefaultOptions<T extends Partial<BrowserClientOptions>>(optionsArg: T): T;
export {};
//# sourceMappingURL=client.d.ts.map