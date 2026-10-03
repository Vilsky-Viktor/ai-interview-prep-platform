import type { StackFrame } from '@sentry/core';
type StackFrameIteratee = (frame: StackFrame) => StackFrame;
interface RewriteFramesOptions {
    root?: string;
    prefix?: string;
    iteratee?: StackFrameIteratee;
}
export declare const customRewriteFramesIntegration: (options?: RewriteFramesOptions) => {
    name: string;
} | (import("@sentry/core").Integration & {
    name: "RewriteFrames";
});
export declare const rewriteFramesIntegration: (options?: RewriteFramesOptions | undefined) => import("@sentry/core").Integration & {
    name: string;
};
export {};
//# sourceMappingURL=rewriteFramesIntegration.d.ts.map