import type { Options as SentryBuildPluginOptions } from '@sentry/bundler-plugins/core';
import type { SentryBuildOptions } from './types';
declare const LOGGER_PREFIXES: {
    readonly 'webpack-nodejs': '[@sentry/nextjs - Node.js]';
    readonly 'webpack-edge': '[@sentry/nextjs - Edge]';
    readonly 'webpack-client': '[@sentry/nextjs - Client]';
    readonly 'after-production-compile-webpack': '[@sentry/nextjs - After Production Compile (Webpack)]';
    readonly 'after-production-compile-turbopack': '[@sentry/nextjs - After Production Compile (Turbopack)]';
};
type BuildTool = keyof typeof LOGGER_PREFIXES;
/**
 * Normalizes Windows paths to POSIX format for glob patterns
 */
export declare function normalizePathForGlob(distPath: string): string;
/**
 * Get Sentry Build Plugin options for both webpack and turbopack builds.
 * These options can be used in two ways:
 * 1. The options can be built in a single operation after the production build completes
 * 2. The options can be built in multiple operations, one for each webpack build
 */
export declare function getBuildPluginOptions({ sentryBuildOptions, releaseName, distDirAbsPath, buildTool, useRunAfterProductionCompileHook, }: {
    sentryBuildOptions: SentryBuildOptions;
    releaseName: string | undefined;
    distDirAbsPath: string;
    buildTool: BuildTool;
    useRunAfterProductionCompileHook?: boolean;
}): SentryBuildPluginOptions;
export {};
//# sourceMappingURL=getBuildPluginOptions.d.ts.map