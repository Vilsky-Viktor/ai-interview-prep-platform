/**
 * Instrumented packages verified (via e2e) to bundle correctly, removed from Sentry's own
 * `serverExternalPackages` defaults so the build-time loader can transform them. Everything else
 * stays external and is instrumented by the runtime module hook instead. Deliberately an
 * allowlist — bundling can break packages outright (e.g. `mysql` 2.x under Turbopack).
 */
export declare const BUNDLE_SAFE_INSTRUMENTED_PACKAGES: string[];
/**
 * `@sentry/server-runtime-injection` (where `register.ts` and the bundled orchestrion runtime ship)
 * must stay external: `register.ts` passes its own `__filename`/`import.meta.url` as the `parentURL`
 * for `Module.register()` and resolves the ESM loader hook relative to that same location, so both
 * only work while the code still lives at its real `node_modules` location. Bundled into an app
 * server chunk instead, they would resolve from the chunk's output location, where neither the hook
 * nor the vendored transformer it loads exists.
 *
 * `@sentry/server-utils` (the barrel + bundler plugins) is NOT here — it is meant to be bundled; the
 * build-time snippet's `@sentry/server-utils` import is handled separately by the code-transform.
 */
export declare const ORCHESTRION_RUNTIME_EXTERNAL_PACKAGES: string[];
/** Remove the given packages from a `serverExternalPackages` list. */
export declare function filterInstrumentedExternals(externals: string[], packagesToBundle: string[]): string[];
/** The forwarder specifier mirroring `request`: `<pkg>/a/b` → `…/orchestrion-runtime/a/b`. */
export declare function getOrchestrionForwarderSpecifier(request: string, externalPackage: string): string;
/**
 * A webpack `externals` array entry that keeps {@link ORCHESTRION_RUNTIME_EXTERNAL_PACKAGES}
 * external, via the matching forwarder under {@link ORCHESTRION_FORWARDER_PREFIX}.
 *
 * `serverExternalPackages` can't do this: Next only externalizes a package whose bare specifier
 * also resolves from the project root (`resolveExternal`'s base-resolve check in
 * `next/dist/build/handle-externals.js`), and under isolated installs this one doesn't — so Next
 * silently bundles it, breaking the `Module.register` self-reference described on
 * {@link ORCHESTRION_RUNTIME_EXTERNAL_PACKAGES}.
 *
 * Must be placed *before* Next's own externals handler: webpack calls array entries in order and
 * stops at the first result.
 */
export declare function externalizeOrchestrionRuntimePackages({ request, }: {
    request?: string;
}): Promise<string | undefined>;
//# sourceMappingURL=diagnosticsChannelInjection.d.ts.map