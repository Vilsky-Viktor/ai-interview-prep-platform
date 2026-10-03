import type { VercelCronsConfig } from '../../common/types';
import type { RouteManifest } from '../manifest/types';
import type { NextConfigObject, SentryBuildOptions, TurbopackMatcherWithRule, TurbopackOptions } from '../types';
/**
 * Construct a Turbopack config object from a Next.js config object and a Turbopack options object.
 *
 * @param userNextConfig - The Next.js config object.
 * @param userSentryOptions - The Sentry build options object.
 * @param routeManifest - The route manifest object.
 * @param nextJsVersion - The Next.js version.
 * @param vercelCronsConfig - The Vercel crons configuration from vercel.json.
 * @returns The Turbopack config object.
 */
export declare function constructTurbopackConfig({ userNextConfig, userSentryOptions, routeManifest, nextJsVersion, vercelCronsConfig, }: {
    userNextConfig: NextConfigObject;
    userSentryOptions?: SentryBuildOptions;
    routeManifest?: RouteManifest;
    nextJsVersion?: string;
    vercelCronsConfig?: VercelCronsConfig;
}): TurbopackOptions;
/**
 * Safely add a Turbopack rule to the existing rules.
 *
 * @param existingRules - The existing rules.
 * @param matcher - The matcher for the rule.
 * @param rule - The rule to add.
 * @returns The updated rules object.
 */
export declare function safelyAddTurbopackRule(existingRules: TurbopackOptions['rules'], { matcher, rule }: TurbopackMatcherWithRule): TurbopackOptions['rules'];
//# sourceMappingURL=constructTurbopackConfig.d.ts.map