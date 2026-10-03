import type { RouteManifest } from './types';
/**
 * Param names that are treated as an optional i18n prefix, so that unprefixed paths of the default
 * locale (e.g. next-intl's `localePrefix: 'as-needed'`) still match their localized route pattern.
 */
export declare const DEFAULT_LOCALE_PARAM_NAMES: string[];
export type CreateRouteManifestOptions = {
    appDirPath?: string;
    /**
     * Whether to include route groups (e.g., (auth-layout)) in the final route paths.
     * By default, route groups are stripped from paths following Next.js convention.
     */
    includeRouteGroups?: boolean;
    /**
     * Base path for the application, if any. This will be prefixed to all routes.
     */
    basePath?: string;
    /**
     * Param names to treat as an optional i18n prefix. Replaces (does not extend) the defaults.
     * Pass an empty array to disable optional prefix matching entirely.
     */
    localeParamNames?: string[];
    /**
     * Suppresses the SDK's own build-time logs.
     */
    silent?: boolean;
};
/**
 * Returns a route manifest for the given app directory
 */
export declare function createRouteManifest(options?: CreateRouteManifestOptions): RouteManifest;
//# sourceMappingURL=createRouteManifest.d.ts.map