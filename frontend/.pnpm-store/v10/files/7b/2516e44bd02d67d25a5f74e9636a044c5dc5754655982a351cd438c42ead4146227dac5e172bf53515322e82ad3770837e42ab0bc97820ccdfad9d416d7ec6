/**
 * Diagnostics-channel-based `pg` (node-postgres) integration.
 *
 * Subscribes to the `orchestrion:pg:query`/`:connect` and
 * `orchestrion:pg-pool:connect` diagnostics_channels that Sentry's code
 * transform injects into `pg`'s `Client.prototype.query`/`connect`
 * and `pg-pool`'s `Pool.prototype.connect`. Requires the Sentry runtime
 * hook or bundler plugin to be active.
 */
export declare const postgresIntegration: (options?: {
    ignoreConnectSpans?: boolean;
} | undefined) => import("@sentry/core").Integration & {
    name: "Postgres";
};
//# sourceMappingURL=postgres.d.ts.map