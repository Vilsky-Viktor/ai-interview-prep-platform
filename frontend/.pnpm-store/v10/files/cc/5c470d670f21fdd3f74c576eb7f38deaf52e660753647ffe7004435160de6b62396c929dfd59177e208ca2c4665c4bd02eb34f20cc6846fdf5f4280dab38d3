import type { NextConfigObject, SentryBuildOptions } from '../types';
/**
 * Adds Sentry-related build-time variables to `nextConfig.env`.
 *
 * Note: this mutates `userNextConfig`.
 *
 * @param userNextConfig - The user's Next.js config object
 * @param userSentryOptions - The Sentry build options passed to `withSentryConfig`
 * @param releaseName - The resolved release name, if any
 * @param projectDir - The Next.js project root
 */
export declare function setUpBuildTimeVariables(userNextConfig: NextConfigObject, userSentryOptions: SentryBuildOptions, releaseName: string | undefined, projectDir?: string): void;
/**
 * Returns the current git SHA (HEAD), if available.
 *
 * This is a best-effort helper and returns `undefined` if git isn't available or the cwd isn't a git repo.
 */
export declare function getGitRevision(): string | undefined;
/**
 * Reads the project's `instrumentation-client.(js|ts)` file contents, if present.
 *
 * @returns The file contents, or `undefined` if the file can't be found/read
 */
export declare function getInstrumentationClientFileContents(): string | void;
//# sourceMappingURL=buildTime.d.ts.map