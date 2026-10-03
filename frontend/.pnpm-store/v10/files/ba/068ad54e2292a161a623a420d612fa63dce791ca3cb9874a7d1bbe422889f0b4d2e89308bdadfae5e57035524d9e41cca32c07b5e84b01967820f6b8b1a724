import type { LoaderThis } from './types';
export type ModuleMetadataInjectionLoaderOptions = {
    applicationKey: string;
};
/**
 * Inject `_sentryModuleMetadata` into every module so that the
 * `thirdPartyErrorFilterIntegration` can tell first-party code from
 * third-party code.
 *
 * This is the Turbopack equivalent of what `@sentry/bundler-plugins/webpack` does
 * via its `moduleMetadata` option.
 *
 * Options:
 *   - `applicationKey`: The application key used to tag first-party modules.
 */
export default function moduleMetadataInjectionLoader(this: LoaderThis<ModuleMetadataInjectionLoaderOptions>, userCode: string): string;
//# sourceMappingURL=moduleMetadataInjectionLoader.d.ts.map