import { ServerRuntimeClient } from '@sentry/core/server';
import type { VercelEdgeClientOptions } from './types';
import { type SentryTracerProvider } from '@sentry/opentelemetry';
/**
 * The Sentry Vercel Edge Runtime SDK Client.
 *
 * @see VercelEdgeClientOptions for documentation on configuration options.
 * @see ServerRuntimeClient for usage documentation.
 */
export declare class VercelEdgeClient extends ServerRuntimeClient<VercelEdgeClientOptions> {
    traceProvider: SentryTracerProvider | undefined;
    /**
     * Creates a new Vercel Edge Runtime SDK instance.
     * @param options Configuration options for this SDK.
     */
    constructor(options: VercelEdgeClientOptions);
    flush(timeout?: number): Promise<boolean>;
}
//# sourceMappingURL=client.d.ts.map