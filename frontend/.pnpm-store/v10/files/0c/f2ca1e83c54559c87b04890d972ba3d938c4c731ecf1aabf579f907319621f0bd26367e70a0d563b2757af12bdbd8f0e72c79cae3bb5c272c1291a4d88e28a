export interface ServerReference {
    $$typeof: symbol;
    $$id: string;
}
export type ServerFunction = ServerReference & ((...args: unknown[]) => Promise<unknown>);
/**
 * Check if the function is a use cache function.
 *
 * @param value - The function to check.
 * @returns true if the function is a use cache function, false otherwise.
 */
export declare function isUseCacheFunction<T>(value: T & Partial<ServerReference>): value is T & ServerFunction;
//# sourceMappingURL=isUseCacheFunction.d.ts.map