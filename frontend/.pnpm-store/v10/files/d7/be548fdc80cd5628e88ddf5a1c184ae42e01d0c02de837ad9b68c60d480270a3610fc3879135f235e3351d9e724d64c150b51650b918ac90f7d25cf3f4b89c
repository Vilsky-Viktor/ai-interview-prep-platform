import type { NextPageContext } from 'next';
type ContextOrProps = {
    req?: NextPageContext['req'];
    res?: NextPageContext['res'];
    err?: NextPageContext['err'] | string;
    pathname?: string;
    statusCode?: number;
};
/**
 * Capture the exception passed by nextjs to the `_error` page, adding context data as appropriate.
 *
 * This will not capture the exception if the status code is < 500 or if the pathname is not provided and will thus not return an event ID.
 *
 * @param contextOrProps The data passed to either `getInitialProps` or `render` by nextjs
 * @returns The Sentry event ID, or `undefined` if no event was captured
 */
export declare function captureUnderscoreErrorException(contextOrProps: ContextOrProps): Promise<string | undefined>;
export {};
//# sourceMappingURL=_error.d.ts.map