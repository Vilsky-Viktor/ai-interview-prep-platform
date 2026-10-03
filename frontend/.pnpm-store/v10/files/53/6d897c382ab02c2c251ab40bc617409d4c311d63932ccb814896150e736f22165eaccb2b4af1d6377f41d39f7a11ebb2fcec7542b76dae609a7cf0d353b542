Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const debugBuild = require('../debug-build.js');
const helpers = require('../helpers.js');
const UIProfiler = require('./UIProfiler.js');

const INTEGRATION_NAME = "BrowserProfiling";
const _browserProfilingIntegration = (() => {
  return {
    name: INTEGRATION_NAME,
    setup(client) {
      const options = client.getOptions();
      const profiler = new UIProfiler.UIProfiler();
      if (!options.profileLifecycle) {
        options.profileLifecycle = "manual";
      }
      const activeSpan = core.getActiveSpan();
      const rootSpan = activeSpan && core.getRootSpan(activeSpan);
      const lifecycleMode = options.profileLifecycle;
      client.on("startUIProfiler", () => profiler.start());
      client.on("stopUIProfiler", () => profiler.stop());
      if (lifecycleMode === "manual") {
        profiler.initialize(client);
      } else if (lifecycleMode === "trace") {
        if (!core.hasSpansEnabled(options)) {
          debugBuild.DEBUG_BUILD && core.debug.warn(
            "[Profiling] `profileLifecycle` is 'trace' but tracing is disabled. Set a `tracesSampleRate` or `tracesSampler` to enable span tracing."
          );
          return;
        }
        profiler.initialize(client);
        if (rootSpan) {
          profiler.notifyRootSpanActive(rootSpan);
        }
        helpers.WINDOW.setTimeout(() => {
          const laterActiveSpan = core.getActiveSpan();
          const laterRootSpan = laterActiveSpan && core.getRootSpan(laterActiveSpan);
          if (laterRootSpan) {
            profiler.notifyRootSpanActive(laterRootSpan);
          }
        }, 0);
      }
    }
  };
});
const browserProfilingIntegration = core.defineIntegration(_browserProfilingIntegration);

exports.browserProfilingIntegration = browserProfilingIntegration;
//# sourceMappingURL=integration.js.map
