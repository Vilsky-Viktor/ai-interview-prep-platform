import type { Span } from '@sentry/core';
/**
 * Checks if the incoming request is a Vercel Queue consumer callback (push mode)
 * and enriches the http.server span with OTel messaging semantic attributes.
 *
 * Vercel Queues push delivery sends a CloudEvent POST with the header:
 *   ce-type: com.vercel.queue.v2beta
 * along with ce-vqs* headers carrying queue metadata.
 */
export declare function maybeEnrichQueueConsumerSpan(span: Span): void;
/**
 * Checks if an outgoing http.client span targets the Vercel Queues API
 * and enriches it with OTel messaging semantic attributes (producer side).
 *
 * The Vercel Queues API lives at *.vercel-queue.com/api/v3/topic/<topic>.
 * We use domain-based detection to avoid false positives from user routes.
 */
export declare function maybeEnrichQueueProducerSpan(span: Span): void;
/**
 * Cleans up the internal marker attribute from enriched queue spans on end.
 */
export declare function maybeCleanupQueueSpan(span: Span): void;
//# sourceMappingURL=vercelQueuesMonitoring.d.ts.map