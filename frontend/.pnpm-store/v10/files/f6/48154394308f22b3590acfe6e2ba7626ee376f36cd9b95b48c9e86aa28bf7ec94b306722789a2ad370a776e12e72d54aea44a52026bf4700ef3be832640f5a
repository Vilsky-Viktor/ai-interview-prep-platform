export interface MutableRootSpan {
    attributes: Record<string, unknown>;
    getName(): string | undefined;
    setName(name: string): void;
    setOp(op: string): void;
}
/**
 * Normalizes name, op and source for the root span of a pages-router API route on the Edge runtime.
 *
 * We no longer create this transaction ourselves in `wrapApiHandlerWithSentry`, so the root span is the
 * Next.js `Node.runHandler` span. Next.js names it `executing api route (pages) /some/route`, which we
 * turn into a proper `${METHOD} ${route}` transaction with the `http.server` op and `route` source.
 *
 * Applied from both `preprocessEvent` (legacy transaction events) and `processSegmentSpan` (streamed spans),
 * mirroring how `enhanceMiddlewareRootSpan` is wired.
 */
export declare function enhanceRunHandlerRootSpan(span: MutableRootSpan): void;
//# sourceMappingURL=enhanceRunHandlerRootSpan.d.ts.map