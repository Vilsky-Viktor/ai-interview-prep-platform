/**
 * web-vitals 5.1.0 switched listeners to be added on the window rather than the document.
 * Instead of having to check for window/document every time we add a listener, we can use this function.
 */
export declare function addPageListener(type: string, listener: EventListener, options?: boolean | AddEventListenerOptions): void;
/**
 * web-vitals 5.1.0 switched listeners to be removed from the window rather than the document.
 * Instead of having to check for window/document every time we remove a listener, we can use this function.
 */
export declare function removePageListener(type: string, listener: EventListener, options?: boolean | AddEventListenerOptions): void;
export declare const getNavigationEntry: (checkResponseStart?: boolean) => PerformanceNavigationTiming | void;
export declare const getActivationStart: () => number;
export interface OnHiddenCallback {
    (event: Event): void;
}
export declare const onHidden: (cb: OnHiddenCallback) => void;
export declare const getVisibilityWatcher: () => {
    readonly firstHiddenTime: number;
    onHidden(cb: () => void): void;
};
/**
 * Runs the passed callback during the next idle period, or immediately
 * if the browser's visibility state is (or becomes) hidden.
 */
export declare const whenIdleOrHidden: (cb: () => void) => void;
//# sourceMappingURL=utils.d.ts.map