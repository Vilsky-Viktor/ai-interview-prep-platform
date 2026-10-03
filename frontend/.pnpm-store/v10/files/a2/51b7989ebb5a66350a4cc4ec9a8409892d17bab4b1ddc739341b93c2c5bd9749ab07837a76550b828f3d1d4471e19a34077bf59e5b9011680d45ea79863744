import { LRUMap } from '@sentry/core';
/**
 * Cache for ISR/SSG route checks. Exported for testing purposes.
 * @internal
 */
export declare const IS_ISR_SSG_ROUTE_CACHE: LRUMap<string, boolean>;
/**
 * Check if the current page is an ISR/SSG route by checking the route manifest.
 * @internal Exported for testing purposes.
 */
export declare function isIsrSsgRoute(pathname: string): boolean;
/**
 * Remove sentry-trace and baggage meta tags from the DOM if this is an ISR/SSG page.
 * This prevents the browser tracing integration from using stale/cached trace IDs.
 */
export declare function removeIsrSsgTraceMetaTags(): void;
//# sourceMappingURL=isrRoutingTracing.d.ts.map