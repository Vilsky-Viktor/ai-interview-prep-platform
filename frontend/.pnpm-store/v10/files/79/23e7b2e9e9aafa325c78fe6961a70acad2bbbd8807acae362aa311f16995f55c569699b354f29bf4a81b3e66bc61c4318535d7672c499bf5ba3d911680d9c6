type BFCacheFrame = 'top' | 'child';
interface BFCacheMetricsIntegrationOptions {
    /**
     * Maximum number of not-restored reasons to emit per miss.
     *
     * By default every reason is reported. Set this to cap the number emitted per miss.
     * Values below 1 are clamped to 1.
     */
    maxReasons: number;
}
interface NotRestoredReason {
    reason?: string;
}
interface NotRestoredReasons {
    children?: NotRestoredReasons[] | null;
    reasons?: (NotRestoredReason | string)[] | null;
}
interface CollectedReason {
    reason: string;
    frame: BFCacheFrame;
}
/**
 * Captures bfcache hit/miss counters and Chromium notRestoredReasons when available.
 */
export declare const bfcacheMetricsIntegration: (options?: Partial<BFCacheMetricsIntegrationOptions> | undefined) => import("@sentry/core").Integration & {
    name: string;
};
/**
 * Resolves the configured `maxReasons` cap. Reports every reason by default and clamps values below 1 to 1,
 * since a cap under 1 would silently drop all reasons.
 *
 * Exported for tests only.
 */
export declare function _resolveMaxReasons(maxReasons: number | undefined): number;
/**
 * Flattens the (possibly nested) bfcache `notRestoredReasons` tree into a capped list of reasons.
 *
 * Exported for tests only.
 */
export declare function _collectNotRestoredReasons(notRestoredReasons: NotRestoredReasons | null | undefined, maxReasons: number): CollectedReason[];
export {};
//# sourceMappingURL=bfcacheMetrics.d.ts.map