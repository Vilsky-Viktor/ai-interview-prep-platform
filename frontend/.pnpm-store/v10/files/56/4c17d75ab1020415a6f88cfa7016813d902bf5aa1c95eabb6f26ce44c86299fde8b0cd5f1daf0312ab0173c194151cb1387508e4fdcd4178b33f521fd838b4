interface BrowserSessionOptions {
    /**
     * Controls the session lifecycle - when new sessions are created.
     *
     * - `'page'`: A session is created once when the page is loaded. Session is not
     *   updated on navigation. This is the default behavior.
     * - `'route'`: A session is created on page load and on every navigation.
     *
     * @default 'page'
     */
    lifecycle?: 'route' | 'page';
}
/**
 * When added, automatically creates sessions which allow you to track adoption and crashes (crash free rate) in your Releases in Sentry.
 * More information: https://docs.sentry.io/product/releases/health/
 *
 * Note: In order for session tracking to work, you need to set up Releases: https://docs.sentry.io/product/releases/
 */
export declare const browserSessionIntegration: (options?: BrowserSessionOptions | undefined) => import("@sentry/core").Integration & {
    name: "BrowserSession";
};
export {};
//# sourceMappingURL=browsersession.d.ts.map