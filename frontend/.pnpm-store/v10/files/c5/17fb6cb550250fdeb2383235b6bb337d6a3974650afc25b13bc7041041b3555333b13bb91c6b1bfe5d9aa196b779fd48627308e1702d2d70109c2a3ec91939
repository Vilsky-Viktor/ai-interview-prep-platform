import type { FetchBreadcrumbHint, HandlerDataFetch } from '@sentry/core';
import type { XhrBreadcrumbHint } from '@sentry/core/browser';
import { GLOBAL_OBJ } from '@sentry/core';
export declare const WINDOW: typeof GLOBAL_OBJ & Omit<Window, 'document'> & Partial<Pick<Window, 'document'>>;
export type NetworkMetaWarning = 'MAYBE_JSON_TRUNCATED' | 'TEXT_TRUNCATED' | 'URL_SKIPPED' | 'BODY_PARSE_ERROR' | 'BODY_PARSE_TIMEOUT' | 'UNPARSEABLE_BODY_TYPE';
type RequestBody = null | Blob | BufferSource | FormData | URLSearchParams | string;
export type XhrHint = XhrBreadcrumbHint & {
    xhr: XMLHttpRequest & SentryWrappedXMLHttpRequest;
    input?: RequestBody;
};
export type FetchHint = FetchBreadcrumbHint & {
    input: HandlerDataFetch['args'];
    response: Response;
};
type XHRSendInput = unknown;
export interface SentryWrappedXMLHttpRequest {
    __sentry_xhr_v3__?: SentryXhrData;
    __sentry_own_request__?: boolean;
    __sentry_xhr_span_id__?: string;
    setRequestHeader?: (key: string, val: string) => void;
    getResponseHeader?: (key: string) => string | null;
}
export interface SentryXhrData {
    method: string;
    url: string;
    status_code?: number;
    body?: XHRSendInput;
    request_body_size?: number;
    response_body_size?: number;
    request_headers: Record<string, string>;
}
export interface HandlerDataXhr {
    xhr: SentryWrappedXMLHttpRequest;
    startTimestamp?: number;
    endTimestamp?: number;
    error?: unknown;
    virtualError?: unknown;
}
export interface HandlerDataDom {
    event: object | {
        target: object;
    };
    name: string;
    global?: boolean;
}
export interface HandlerDataHistory {
    /** The full URL of the previous page */
    from: string | undefined;
    /** The full URL of the new page */
    to: string;
}
export {};
//# sourceMappingURL=types.d.ts.map