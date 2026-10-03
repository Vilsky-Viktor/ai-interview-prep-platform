type ComponentRouteParams = Record<string, string> | undefined;
type HeadersDict = Record<string, string> | undefined;
/**
 * Replaces route parameters in a path template with their values
 * @param path - The path template containing parameters in [paramName] format
 * @param params - Optional route parameters to replace in the template
 * @returns The path with parameters replaced
 */
export declare function substituteRouteParams(path: string, params?: ComponentRouteParams): string;
/**
 * Normalizes a path by removing route groups
 * @param path - The path to normalize
 * @returns The normalized path
 */
export declare function sanitizeRoutePath(path: string): string;
/**
 * Constructs a full URL from the component route, parameters, and headers.
 *
 * @param componentRoute - The route template to construct the URL from
 * @param params - Optional route parameters to replace in the template
 * @param headersDict - Optional headers containing protocol and host information
 * @param pathname - Optional pathname coming from parent span "http.target"
 * @returns A sanitized URL string
 */
export declare function buildUrlFromComponentRoute(componentRoute: string, params?: ComponentRouteParams, headersDict?: HeadersDict, pathname?: string): string;
/**
 * Returns a sanitized URL string from the referer header if it exists and is valid.
 *
 * @param headersDict - Optional headers containing the referer
 * @returns A sanitized URL string or undefined if referer is missing/invalid
 */
export declare function extractSanitizedUrlFromRefererHeader(headersDict?: HeadersDict): string | undefined;
/**
 * Returns a sanitized URL string using the referer header if available,
 * otherwise constructs the URL from the component route, params, and headers.
 *
 * @param componentRoute - The route template to construct the URL from
 * @param params - Optional route parameters to replace in the template
 * @param headersDict - Optional headers containing protocol, host, and referer
 * @param pathname - Optional pathname coming from root span "http.target"
 * @returns A sanitized URL string
 */
export declare function getSanitizedRequestUrl(componentRoute: string, params?: ComponentRouteParams, headersDict?: HeadersDict, pathname?: string): string;
export {};
//# sourceMappingURL=urls.d.ts.map