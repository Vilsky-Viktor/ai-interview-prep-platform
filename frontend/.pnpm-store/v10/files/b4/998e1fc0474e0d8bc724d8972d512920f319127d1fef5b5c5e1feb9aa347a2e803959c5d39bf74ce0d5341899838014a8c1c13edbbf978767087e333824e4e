import type { Client, Span } from '@sentry/core';
/**
 * Listens for events on which we want to collect a previously accumulated web vital value.
 * Currently, this includes:
 *
 * - pagehide (i.e. user minimizes browser window, hides tab, etc)
 * - soft navigation (we only care about the vital of the initially loaded route)
 *
 * As a "side-effect", this function will also collect the pageload span.
 *
 * @param collectorCallback the callback to be called when the first of these events is triggered. It is passed the
 * pageload span, which the web vital span is parented to.
 */
export declare function listenForWebVitalReportEvents(client: Client, collectorCallback: (pageloadSpan: Span) => void): void;
//# sourceMappingURL=reportEvents.d.ts.map