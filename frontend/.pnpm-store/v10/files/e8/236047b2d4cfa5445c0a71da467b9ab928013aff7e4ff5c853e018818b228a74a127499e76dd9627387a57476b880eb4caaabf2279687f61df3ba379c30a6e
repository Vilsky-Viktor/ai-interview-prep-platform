import type { Event, Primitive } from '@sentry/core';
type GlobalHandlersIntegrationsOptionKeys = 'onerror' | 'onunhandledrejection';
type GlobalHandlersIntegrations = Record<GlobalHandlersIntegrationsOptionKeys, boolean>;
export declare const globalHandlersIntegration: (options?: Partial<GlobalHandlersIntegrations> | undefined) => import("@sentry/core").Integration & {
    name: "GlobalHandlers";
};
/**
 *
 */
export declare function _getUnhandledRejectionError(error: unknown): unknown;
/**
 * Create an event from a promise rejection where the `reason` is a primitive.
 *
 * @param reason: The `reason` property of the promise rejection
 * @returns An Event object with an appropriate `exception` value
 */
export declare function _eventFromRejectionWithPrimitive(reason: Primitive): Event;
/**
 * Adds a frame built from the error location when the event has none.
 */
export declare function _enhanceEventWithInitialFrame(event: Event, url: string | undefined, lineno: number | undefined, colno: number | undefined): Event;
export {};
//# sourceMappingURL=globalhandlers.d.ts.map