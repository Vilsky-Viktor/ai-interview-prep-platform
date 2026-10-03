import type { SentryBuildOptions } from './types';
/**
 * This function is called by Next.js after the production build is complete.
 * It is used to upload sourcemaps to Sentry.
 */
export declare function handleRunAfterProductionCompile({ releaseName, distDir, buildTool, usesNativeDebugIds, sriEnabled, }: {
    releaseName?: string;
    distDir: string;
    buildTool: 'webpack' | 'turbopack';
    usesNativeDebugIds?: boolean;
    sriEnabled?: boolean;
}, sentryBuildOptions: SentryBuildOptions): Promise<void>;
/**
 * Strips sourceMappingURL comments from all JS/MJS/CJS/CSS files in the given directory.
 * This prevents browsers from requesting deleted .map files.
 */
export declare function stripSourceMappingURLComments(staticDir: string, { debug, silent }?: Pick<SentryBuildOptions, 'debug' | 'silent'>): Promise<void>;
//# sourceMappingURL=handleRunAfterProductionCompile.d.ts.map