import { browserTracingIntegration } from '@sentry/browser';
import type { Integration } from '@sentry/core';
import type { ReactElement } from 'react';
import * as React from 'react';
import type { Action, Location } from './types';
type Match = {
    path: string;
    url: string;
    params: Record<string, any>;
    isExact: boolean;
};
export type RouterHistory = {
    location?: Location;
    listen?(cb: (location: Location, action: Action) => void): void;
} & Record<string, any>;
export type RouteConfig = {
    [propName: string]: unknown;
    path?: string | string[];
    exact?: boolean;
    component?: ReactElement;
    routes?: RouteConfig[];
};
export type MatchPath = (pathname: string, props: string | string[] | any, parent?: Match | null) => Match | null;
interface ReactRouterOptions {
    history: RouterHistory;
    routes?: RouteConfig[];
    matchPath?: MatchPath;
}
/**
 * A browser tracing integration that uses React Router v4 to instrument navigations.
 * Expects `history` (and optionally `routes` and `matchPath`) to be passed as options.
 */
export declare function reactRouterV4BrowserTracingIntegration(options: Parameters<typeof browserTracingIntegration>[0] & ReactRouterOptions): Integration;
/**
 * A browser tracing integration that uses React Router v5 to instrument navigations.
 * Expects `history` (and optionally `routes` and `matchPath`) to be passed as options.
 */
export declare function reactRouterV5BrowserTracingIntegration(options: Parameters<typeof browserTracingIntegration>[0] & ReactRouterOptions): Integration;
/**
 * A higher-order component that adds Sentry routing instrumentation to a React Router v4 or v5 `Route` component.
 * When the wrapped `Route` matches, the active pageload/navigation span is renamed to the parameterized route path.
 *
 * The wrapped `Route` must be rendered inside a `Switch`, since the match is read from the `computedMatch` prop
 * that only `Switch` passes down. For React Router v6 and later, use `wrapReactRouterRouting` instead.
 *
 * @example
 * ```jsx
 * const SentryRoute = Sentry.withSentryRouting(Route);
 *
 * <Switch>
 *   <SentryRoute path="/users/:id" component={User} />
 * </Switch>
 * ```
 */
export declare function withSentryRouting<P extends Record<string, any>, R extends React.ComponentType<P>>(Route: R): R;
export {};
//# sourceMappingURL=reactrouter.d.ts.map