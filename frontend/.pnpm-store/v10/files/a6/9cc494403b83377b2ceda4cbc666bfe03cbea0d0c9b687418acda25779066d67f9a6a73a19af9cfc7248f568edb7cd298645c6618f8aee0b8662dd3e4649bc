import type { Span } from '@sentry/core';
interface InteractionContext {
    span: Span | undefined;
    elementName: string;
}
/** What `htmlTreeAsString` returns when it cannot describe the target. */
export declare const UNKNOWN_ELEMENT_NAME = "<unknown>";
/**
 * 60 seconds is the maximum for a plausible INP value
 * (source: Me)
 */
export declare const MAX_PLAUSIBLE_INP_DURATION = 60;
export type InteractionType = 'click' | 'hover' | 'drag' | 'press';
export declare const INP_ENTRY_MAP: Record<string, InteractionType>;
/**
 * Look up a cached interaction context (element name + root span) by interactionId.
 * Returns undefined if no context was cached for this interaction.
 */
export declare function getCachedInteractionContext(interactionId: number | undefined): InteractionContext | undefined;
/**
 * Register a listener to cache route information for INP interactions.
 */
export declare function registerInpInteractionListener(): void;
export {};
//# sourceMappingURL=inp.d.ts.map