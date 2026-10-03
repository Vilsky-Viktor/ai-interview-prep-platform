import type { EdgeRouteHandler } from '../edge/types';
/**
 * Wraps Next.js middleware with Sentry error instrumentation.
 *
 * The middleware transaction itself is created by Next.js' native OpenTelemetry instrumentation
 * (the `Middleware.execute` span, normalized by `enhanceMiddlewareRootSpan`), so this wrapper no
 * longer starts its own span. It only forks an isolation scope, captures errors, and flushes.
 *
 * @param middleware The middleware handler.
 * @returns a wrapped middleware handler.
 */
export declare function wrapMiddlewareWithSentry<H extends EdgeRouteHandler>(middleware: H): (...params: Parameters<H>) => Promise<ReturnType<H>>;
//# sourceMappingURL=wrapMiddlewareWithSentry.d.ts.map