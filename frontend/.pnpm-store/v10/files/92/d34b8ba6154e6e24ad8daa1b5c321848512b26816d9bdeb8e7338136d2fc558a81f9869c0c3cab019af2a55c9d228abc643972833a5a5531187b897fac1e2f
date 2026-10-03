import { GLOBAL_OBJ, debug, uuid4, browserPerformanceTimeOrigin, getClient, getDebugImagesForResources } from '@sentry/core';
import { DEBUG_BUILD } from '../debug-build.js';
import { WINDOW } from '../helpers.js';

const isMainThread = "window" in GLOBAL_OBJ && GLOBAL_OBJ.window === GLOBAL_OBJ && typeof importScripts === "undefined";
const PROFILER_THREAD_ID_STRING = String(0);
const PROFILER_THREAD_NAME = isMainThread ? "main" : "worker";
function createProfileChunkPayload(jsSelfProfile, client, profilerId) {
  if (jsSelfProfile == null) {
    throw new TypeError(
      `Cannot construct profiling event envelope without a valid profile. Got ${jsSelfProfile} instead.`
    );
  }
  const continuousProfile = convertToContinuousProfile(jsSelfProfile);
  const options = client.getOptions();
  const sdk = client.getSdkMetadata?.()?.sdk;
  return {
    chunk_id: uuid4(),
    client_sdk: {
      name: sdk?.name ?? "sentry.javascript.browser",
      version: sdk?.version ?? "0.0.0"
    },
    profiler_id: profilerId || uuid4(),
    platform: "javascript",
    version: "2",
    release: options.release ?? "",
    environment: options.environment ?? "production",
    debug_meta: {
      // function name obfuscation
      images: applyDebugMetadata(jsSelfProfile.resources)
    },
    profile: continuousProfile
  };
}
function validateProfileChunk(chunk) {
  try {
    if (!chunk || typeof chunk !== "object") {
      return { reason: "chunk is not an object" };
    }
    const isHex32 = (val) => typeof val === "string" && /^[a-f0-9]{32}$/.test(val);
    if (!isHex32(chunk.profiler_id)) {
      return { reason: "missing or invalid profiler_id" };
    }
    if (!isHex32(chunk.chunk_id)) {
      return { reason: "missing or invalid chunk_id" };
    }
    if (!chunk.client_sdk) {
      return { reason: "missing client_sdk metadata" };
    }
    const profile = chunk.profile;
    if (!profile) {
      return { reason: "missing profile data" };
    }
    if (!Array.isArray(profile.frames) || !profile.frames.length) {
      return { reason: "profile has no frames" };
    }
    if (!Array.isArray(profile.stacks) || !profile.stacks.length) {
      return { reason: "profile has no stacks" };
    }
    if (!Array.isArray(profile.samples) || !profile.samples.length) {
      return { reason: "profile has no samples" };
    }
    return { valid: true };
  } catch (e) {
    return { reason: `unknown validation error: ${e}` };
  }
}
function convertToContinuousProfile(input) {
  const frames = [];
  for (let i = 0; i < input.frames.length; i++) {
    const frame = input.frames[i];
    if (!frame) {
      continue;
    }
    frames[i] = {
      function: frame.name,
      abs_path: typeof frame.resourceId === "number" ? input.resources[frame.resourceId] : void 0,
      lineno: frame.line,
      colno: frame.column
    };
  }
  const stacks = [];
  for (let i = 0; i < input.stacks.length; i++) {
    const stackHead = input.stacks[i];
    if (!stackHead) {
      continue;
    }
    const list = [];
    let current = stackHead;
    while (current) {
      list.push(current.frameId);
      current = current.parentId === void 0 ? void 0 : input.stacks[current.parentId];
    }
    stacks[i] = list;
  }
  const perfOrigin = browserPerformanceTimeOrigin();
  const origin = typeof performance.timeOrigin === "number" ? performance.timeOrigin : perfOrigin || 0;
  const adjustForOriginChange = origin - (perfOrigin || origin);
  const samples = [];
  for (let i = 0; i < input.samples.length; i++) {
    const sample = input.samples[i];
    if (!sample) {
      continue;
    }
    const timestampSeconds = (origin + (sample.timestamp - adjustForOriginChange)) / 1e3;
    samples[i] = {
      stack_id: sample.stackId ?? 0,
      thread_id: PROFILER_THREAD_ID_STRING,
      timestamp: timestampSeconds
    };
  }
  return {
    frames,
    stacks,
    samples,
    thread_metadata: { [PROFILER_THREAD_ID_STRING]: { name: PROFILER_THREAD_NAME } }
  };
}
function applyDebugMetadata(resource_paths) {
  const client = getClient();
  const options = client?.getOptions();
  const stackParser = options?.stackParser;
  if (!stackParser) {
    return [];
  }
  return getDebugImagesForResources(stackParser, resource_paths);
}
function isValidSampleRate(rate) {
  if (typeof rate !== "number" && typeof rate !== "boolean" || typeof rate === "number" && isNaN(rate)) {
    DEBUG_BUILD && debug.warn(
      `[Profiling] Invalid sample rate. Sample rate must be a boolean or a number between 0 and 1. Got ${JSON.stringify(
        rate
      )} of type ${JSON.stringify(typeof rate)}.`
    );
    return false;
  }
  if (rate === true || rate === false) {
    return true;
  }
  if (rate < 0 || rate > 1) {
    DEBUG_BUILD && debug.warn(`[Profiling] Invalid sample rate. Sample rate must be between 0 and 1. Got ${rate}.`);
    return false;
  }
  return true;
}
let PROFILING_CONSTRUCTOR_FAILED = false;
const MAX_PROFILE_DURATION_MS = 3e4;
function isJSProfilerSupported(maybeProfiler) {
  return typeof maybeProfiler === "function";
}
function startJSSelfProfile() {
  const JSProfilerConstructor = WINDOW.Profiler;
  if (!isJSProfilerSupported(JSProfilerConstructor)) {
    if (DEBUG_BUILD) {
      debug.log("[Profiling] Profiling is not supported by this browser, Profiler interface missing on window object.");
    }
    return;
  }
  const samplingIntervalMS = 10;
  const maxSamples = Math.floor(MAX_PROFILE_DURATION_MS / samplingIntervalMS);
  try {
    return new JSProfilerConstructor({ sampleInterval: samplingIntervalMS, maxBufferSize: maxSamples });
  } catch {
    if (DEBUG_BUILD) {
      debug.log(
        "[Profiling] Failed to initialize the Profiling constructor, this is likely due to a missing 'Document-Policy': 'js-profiling' header."
      );
      debug.log("[Profiling] Disabling profiling for current user session.");
    }
    PROFILING_CONSTRUCTOR_FAILED = true;
  }
  return;
}
function shouldProfileSession(options) {
  if (PROFILING_CONSTRUCTOR_FAILED) {
    if (DEBUG_BUILD) {
      debug.log(
        "[Profiling] Profiling has been disabled for the duration of the current user session as the JS Profiler could not be started."
      );
    }
    return false;
  }
  if (options.profileLifecycle !== "trace" && options.profileLifecycle !== "manual") {
    DEBUG_BUILD && debug.warn("[Profiling] Session not sampled. Invalid `profileLifecycle` option.");
    return false;
  }
  const profileSessionSampleRate = options.profileSessionSampleRate;
  if (!isValidSampleRate(profileSessionSampleRate)) {
    DEBUG_BUILD && debug.warn("[Profiling] Discarding profile because of invalid profileSessionSampleRate.");
    return false;
  }
  if (!profileSessionSampleRate) {
    DEBUG_BUILD && debug.log("[Profiling] Discarding profile because profileSessionSampleRate is not defined or set to 0");
    return false;
  }
  return Math.random() <= profileSessionSampleRate;
}
function setThreadAttributes(span) {
  span.setAttribute("thread.id", PROFILER_THREAD_ID_STRING);
  span.setAttribute("thread.name", PROFILER_THREAD_NAME);
}

export { MAX_PROFILE_DURATION_MS, PROFILER_THREAD_ID_STRING, PROFILER_THREAD_NAME, applyDebugMetadata, createProfileChunkPayload, isValidSampleRate, setThreadAttributes, shouldProfileSession, startJSSelfProfile, validateProfileChunk };
//# sourceMappingURL=utils.js.map
