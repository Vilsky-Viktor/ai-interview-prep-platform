Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const debugBuild = require('../../../debug-build.js');

const unleashIntegration = core.defineIntegration(
  ({ featureFlagClientClass: unleashClientClass }) => {
    return {
      name: "Unleash",
      setupOnce() {
        const unleashClientPrototype = unleashClientClass.prototype;
        core.fill(unleashClientPrototype, "isEnabled", _wrappedIsEnabled);
      },
      processEvent(event, _hint, _client) {
        return core._INTERNAL_copyFlagsFromScopeToEvent(event);
      }
    };
  }
);
function _wrappedIsEnabled(original) {
  return function(...args) {
    const toggleName = args[0];
    const result = original.apply(this, args);
    if (typeof toggleName === "string" && typeof result === "boolean") {
      core._INTERNAL_insertFlagToScope(toggleName, result);
      core._INTERNAL_addFeatureFlagToActiveSpan(toggleName, result);
    } else if (debugBuild.DEBUG_BUILD) {
      core.debug.error(
        `[Feature Flags] UnleashClient.isEnabled does not match expected signature. arg0: ${toggleName} (${typeof toggleName}), result: ${result} (${typeof result})`
      );
    }
    return result;
  };
}

exports.unleashIntegration = unleashIntegration;
//# sourceMappingURL=integration.js.map
