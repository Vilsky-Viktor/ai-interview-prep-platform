Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');

const launchDarklyIntegration = core.defineIntegration(() => {
  return {
    name: "LaunchDarkly",
    processEvent(event, _hint, _client) {
      return core._INTERNAL_copyFlagsFromScopeToEvent(event);
    }
  };
});
function buildLaunchDarklyFlagUsedHandler() {
  return {
    name: "sentry-flag-auditor",
    type: "flag-used",
    synchronous: true,
    /**
     * Handle a flag evaluation by storing its name and value on the current scope.
     */
    method: (flagKey, flagDetail, _context) => {
      core._INTERNAL_insertFlagToScope(flagKey, flagDetail.value);
      core._INTERNAL_addFeatureFlagToActiveSpan(flagKey, flagDetail.value);
    }
  };
}

exports.buildLaunchDarklyFlagUsedHandler = buildLaunchDarklyFlagUsedHandler;
exports.launchDarklyIntegration = launchDarklyIntegration;
//# sourceMappingURL=integration.js.map
