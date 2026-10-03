Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');

const statsigIntegration = core.defineIntegration(
  ({ featureFlagClient: statsigClient }) => {
    return {
      name: "Statsig",
      setup(_client) {
        statsigClient.on("gate_evaluation", (event) => {
          core._INTERNAL_insertFlagToScope(event.gate.name, event.gate.value);
          core._INTERNAL_addFeatureFlagToActiveSpan(event.gate.name, event.gate.value);
        });
      },
      processEvent(event, _hint, _client) {
        return core._INTERNAL_copyFlagsFromScopeToEvent(event);
      }
    };
  }
);

exports.statsigIntegration = statsigIntegration;
//# sourceMappingURL=integration.js.map
