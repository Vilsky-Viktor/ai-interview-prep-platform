/**
 * Next.js' OTel instrumentation only sets the deprecated `http.status_code` attribute on its request
 * root spans. Backfill the modern `http.response.status_code` from it so downstream consumers that
 * rely on the current convention still see the status code.
 */
export declare function backfillHttpResponseStatusCode(attributes: Record<string, unknown>): void;
//# sourceMappingURL=backfillHttpResponseStatusCode.d.ts.map