import type { Client, PropagationContext, RawAttributes, Span } from '@sentry/core';
import { Scope } from '@sentry/core';
/**
 * Takes a shared (garbage collectable) object between resources, e.g. a headers object shared between Next.js server components and returns a common propagation context.
 *
 * @param commonObject The shared object.
 * @param propagationContext The propagation context that should be shared between all the resources if no propagation context was registered yet.
 * @returns the shared propagation context.
 */
export declare function commonObjectToPropagationContext(commonObject: unknown, propagationContext: PropagationContext): PropagationContext;
/**
 * Takes a shared (garbage collectable) object between resources, e.g. a headers object shared between Next.js server components and returns a common propagation context.
 *
 * @param commonObject The shared object.
 * @param isolationScope The isolationScope that should be shared between all the resources if no isolation scope was created yet.
 * @returns the shared isolation scope.
 */
export declare function commonObjectToIsolationScope(commonObject: unknown): Scope;
/**
 * Checks if the span is a resolve segment span.
 * @param spanAttributes The attributes of the span to check.
 * @returns True if the span is a resolve segment span, false otherwise.
 */
export declare function isResolveSegmentSpan(spanAttributes: RawAttributes<Record<string, unknown>>): boolean;
/**
 * Returns the enhanced name for a resolve segment span.
 * @param segment The segment of the resolve segment span.
 * @param route The route of the resolve segment span.
 * @returns The enhanced name for the resolve segment span.
 */
export declare function getEnhancedResolveSegmentSpanName({ segment, route }: {
    segment: string;
    route: string;
}): string;
/**
 * Maybe enhances the span name for a resolve segment span.
 * If the span is not a resolve segment span, this function does nothing.
 * @param activeSpan The active span.
 * @param spanAttributes The attributes of the span to check.
 * @param rootSpanAttributes The attributes of the according root span.
 */
export declare function maybeEnhanceServerComponentSpanName(activeSpan: Span, spanAttributes: RawAttributes<Record<string, unknown>>, rootSpanAttributes: RawAttributes<Record<string, unknown>>, client: Client): void;
//# sourceMappingURL=tracingUtils.d.ts.map