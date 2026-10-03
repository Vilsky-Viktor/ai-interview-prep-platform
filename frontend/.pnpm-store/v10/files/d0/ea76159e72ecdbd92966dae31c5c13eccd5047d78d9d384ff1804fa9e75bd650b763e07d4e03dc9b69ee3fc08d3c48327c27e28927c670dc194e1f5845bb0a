import type { RouteManifest } from './manifest/types';
import type { NextConfigObject, SentryBuildOptions, WebpackConfigFunction } from './types';
import type { VercelCronsConfigResult } from './withSentryConfig/getFinalConfigObjectUtils';
/**
 * Construct the function which will be used as the nextjs config's `webpack` value.
 *
 * Sets:
 *   - `devtool`, to ensure high-quality sourcemaps are generated
 *   - `entry`, to include user's sentry config files (where `Sentry.init` is called) in the build
 *   - `plugins`, to add SentryWebpackPlugin
 *
 * @param userNextConfig The user's existing nextjs config, as passed to `withSentryConfig`
 * @param userSentryOptions The user's SentryWebpackPlugin config, as passed to `withSentryConfig`
 * @returns The function to set as the nextjs config's `webpack` value
 */
export declare function constructWebpackConfigFunction({ userNextConfig, userSentryOptions, releaseName, routeManifest, nextJsVersion, useRunAfterProductionCompileHook, vercelCronsConfigResult, }: {
    userNextConfig: NextConfigObject;
    userSentryOptions: SentryBuildOptions;
    releaseName: string | undefined;
    routeManifest: RouteManifest | undefined;
    nextJsVersion: string | undefined;
    useRunAfterProductionCompileHook: boolean | undefined;
    vercelCronsConfigResult: VercelCronsConfigResult;
}): WebpackConfigFunction;
//# sourceMappingURL=webpack.d.ts.map