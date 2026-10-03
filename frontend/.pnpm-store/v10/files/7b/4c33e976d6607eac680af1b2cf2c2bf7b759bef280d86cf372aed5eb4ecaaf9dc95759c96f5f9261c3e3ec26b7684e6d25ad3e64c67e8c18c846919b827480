import type { Span } from '@sentry/core';
/**
 * Derive the span status of a Next.js `http.server` root span from its HTTP response status code.
 *
 * Next.js instruments some requests only via its own OTel spans (e.g. turbopack builds, where the
 * route-handler wrapper that would otherwise call `setHttpStatus` is not applied). We used to infer the
 * status from the response code at span end; since that inference was removed, derive it here instead.
 *
 * Only runs when the span status is still `ok`, so an error status set by a wrapper or error handler is
 * never overridden. No-ops when there is no numeric response code or the code maps to `ok`.
 */
export declare function backfillHttpServerStatus(span: Span): void;
//# sourceMappingURL=backfillHttpServerStatus.d.ts.map