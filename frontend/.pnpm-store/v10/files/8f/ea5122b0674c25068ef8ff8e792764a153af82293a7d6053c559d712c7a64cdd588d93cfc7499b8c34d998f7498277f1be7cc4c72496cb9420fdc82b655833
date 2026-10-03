/**
 * Returns the version of Next.js installed in the project, or undefined if it cannot be determined.
 */
export declare function getNextjsVersion(): string | undefined;
/**
 * Checks if the current Next.js version supports the runAfterProductionCompile hook.
 * This hook was introduced in Next.js 15.4.1. (https://github.com/vercel/next.js/pull/77345)
 *
 * @param version - version string to check.
 * @returns true if Next.js version is 15.4.1 or higher
 */
export declare function supportsProductionCompileHook(version: string): boolean;
/**
 * Checks if the current Next.js version supports the `condition` field in Turbopack rules.
 * This field was introduced in Next.js 16.
 *
 * @param version - version string to check.
 * @returns true if Next.js version is 16 or higher
 */
export declare function supportsTurbopackRuleCondition(version: string): boolean;
/**
 * Checks if the current Next.js version supports native debug ids for turbopack.
 * This feature was first introduced in Next.js v15.6.0-canary.36 and marked stable in Next.js v16
 *
 * @param version - version string to check.
 * @returns true if Next.js version supports native debug ids for turbopack builds
 */
export declare function supportsNativeDebugIds(version: string): boolean;
/**
 * Checks if the given Next.js version requires the `experimental.instrumentationHook` option.
 * Next.js 15.0.0 and higher (including certain RC and canary versions) no longer require this option
 * and will print a warning if it is set.
 *
 * @param version - version string to check.
 * @returns true if the version requires the instrumentationHook option to be set
 */
export declare function requiresInstrumentationHook(version: string): boolean;
/**
 * Determines which bundler is actually being used based on environment variables,
 * and CLI flags.
 *
 * @returns 'turbopack' or 'webpack'
 */
export declare function detectActiveBundler(): 'turbopack' | 'webpack';
/**
 * Extract modules from project directory's package.json
 */
export declare function getPackageModules(projectDir: string): Record<string, string>;
//# sourceMappingURL=util.d.ts.map