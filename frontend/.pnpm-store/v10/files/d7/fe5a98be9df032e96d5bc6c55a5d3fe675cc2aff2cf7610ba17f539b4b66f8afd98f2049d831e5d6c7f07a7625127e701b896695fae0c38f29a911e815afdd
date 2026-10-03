import type { Client, DebugImage, ProfileChunk, Span } from '@sentry/core';
import type { BrowserOptions } from '../client';
import type { JSSelfProfile, JSSelfProfiler } from './jsSelfProfiling';
export declare const PROFILER_THREAD_ID_STRING: string;
export declare const PROFILER_THREAD_NAME: string;
/**
 * Create a profile chunk envelope item
 */
export declare function createProfileChunkPayload(jsSelfProfile: JSSelfProfile, client: Client, profilerId?: string): ProfileChunk;
/**
 * Validate a profile chunk against the Sample Format V2 requirements.
 * https://develop.sentry.dev/sdk/telemetry/profiles/sample-format-v2/
 * - Presence of samples, stacks, frames
 * - Required metadata fields
 */
export declare function validateProfileChunk(chunk: ProfileChunk): {
    valid: true;
} | {
    reason: string;
};
/**
 * Applies debug meta data to an event from a list of paths to resources (sourcemaps)
 */
export declare function applyDebugMetadata(resource_paths: ReadonlyArray<string>): DebugImage[];
/**
 * Checks the given sample rate to make sure it is valid type and value (a boolean, or a number between 0 and 1).
 */
export declare function isValidSampleRate(rate: unknown): boolean;
export declare const MAX_PROFILE_DURATION_MS = 30000;
/**
 * Starts the profiler and returns the profiler instance.
 */
export declare function startJSSelfProfile(): JSSelfProfiler | undefined;
/**
 * Determine if a profile should be created for the current session.
 */
export declare function shouldProfileSession(options: BrowserOptions): boolean;
export declare function setThreadAttributes(span: Span): void;
//# sourceMappingURL=utils.d.ts.map