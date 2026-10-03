export interface MutableMiddlewareRootSpan {
    attributes: Record<string, unknown>;
    getName(): string | undefined;
    setName(name: string): void;
    setOp(op: string): void;
}
/**
 * Normalizes the transaction name and op for the root span of a Next.js `Middleware.execute` request.
 *
 * On the Edge runtime, middleware always runs in a detached sandbox, so `Middleware.execute` is the root span.
 * On the Node.js runtime, this is the case since vercel/next.js#95306, where in-process
 * middleware runs in a detached OTel context instead of inside the `BaseServer.handleRequest` span.
 *
 * Older Next.js versions append the full URL to the middleware span name (e.g. `middleware GET /foo?bar=1`),
 * producing high-cardinality transaction names. We collapse the name to `middleware {METHOD}` when possible,
 * and strip query/fragment otherwise.
 */
export declare function enhanceMiddlewareRootSpan(span: MutableMiddlewareRootSpan): void;
//# sourceMappingURL=enhanceMiddlewareRootSpan.d.ts.map