export interface MutableRootSpan {
    attributes: Record<string, unknown>;
    getName(): string | undefined;
    setName(name: string): void;
    setOp(op: string): void;
}
/**
 * Normalizes name, op and source for the root span of a Next.js `BaseServer.handleRequest` request.
 *
 * Called from two places that operate on different shapes of the same underlying root span:
 * - Legacy mode: from `preprocessEvent`, adapted around a transaction `Event` whose `contexts.trace.data`
 *   holds the root span's attributes and whose `event.transaction` is the root span's name.
 * - Streamed mode: from `processSegmentSpan`, adapted around a `StreamedSpanJSON` (the streamed
 *   counterpart of the legacy transaction root) directly.
 *
 * The `MutableRootSpan` adapter hides those differences so the enhancement logic can be shared.
 */
export declare function enhanceHandleRequestRootSpan(span: MutableRootSpan): void;
//# sourceMappingURL=enhanceHandleRequestRootSpan.d.ts.map