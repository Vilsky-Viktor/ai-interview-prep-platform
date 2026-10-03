import { defineIntegration, getActiveSpan, getRootSpan, hasSpansEnabled, debug } from '@sentry/core';
import { DEBUG_BUILD } from '../debug-build.js';
import { WINDOW } from '../helpers.js';
import { UIProfiler } from './UIProfiler.js';

const INTEGRATION_NAME = "BrowserProfiling";
const _browserProfilingIntegration = (() => {
  return {
    name: INTEGRATION_NAME,
    setup(client) {
      const options = client.getOptions();
      const profiler = new UIProfiler();
      if (!options.profileLifecycle) {
        options.profileLifecycle = "manual";
      }
      const activeSpan = getActiveSpan();
      const rootSpan = activeSpan && getRootSpan(activeSpan);
      const lifecycleMode = options.profileLifecycle;
      client.on("startUIProfiler", () => profiler.start());
      client.on("stopUIProfiler", () => profiler.stop());
      if (lifecycleMode === "manual") {
        profiler.initialize(client);
      } else if (lifecycleMode === "trace") {
        if (!hasSpansEnabled(options)) {
          DEBUG_BUILD && debug.warn(
            "[Profiling] `profileLifecycle` is 'trace' but tracing is disabled. Set a `tracesSampleRate` or `tracesSampler` to enable span tracing."
          );
          return;
        }
        profiler.initialize(client);
        if (rootSpan) {
          profiler.notifyRootSpanActive(rootSpan);
        }
        WINDOW.setTimeout(() => {
          const laterActiveSpan = getActiveSpan();
          const laterRootSpan = laterActiveSpan && getRootSpan(laterActiveSpan);
          if (laterRootSpan) {
            profiler.notifyRootSpanActive(laterRootSpan);
          }
        }, 0);
      }
    }
  };
});
const browserProfilingIntegration = defineIntegration(_browserProfilingIntegration);

export { browserProfilingIntegration };
//# sourceMappingURL=integration.js.map
