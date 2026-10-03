Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const moduleNames = require('./module-names.js');

const mastraConstructorConfig = [
  {
    channelName: "mastraConstructor",
    module: {
      name: "@mastra/core",
      versionRange: ">=1.63.2 <2.0.0",
      filePath: /^dist\/(?:[\w.-]+\/)?mastra[\w.-]*\.(?:cjs|mjs|js)$/
    },
    // No `methodName` → class constructor. The `end` message's `self` is the instance.
    functionQuery: { className: "Mastra" }
  }
];
const mastraContextConfig = ["executeWithContext", "executeWithContextSync"].map(
  (functionName) => ({
    channelName: "mastraExecuteWithContext",
    module: {
      name: "@mastra/core",
      versionRange: ">=1.63.2 <2.0.0",
      filePath: /^dist\/observability\/context-storage\.(?:cjs|mjs|js)$/
    },
    functionQuery: { functionName, kind: "Auto" }
  })
);
const mastraConfig = [...mastraConstructorConfig, ...mastraContextConfig];
const mastraModuleNames = moduleNames.getModuleNames(mastraConfig);
const mastraChannels = {
  MASTRA_CONSTRUCTOR: "orchestrion:@mastra/core:mastraConstructor",
  MASTRA_EXECUTE_WITH_CONTEXT: "orchestrion:@mastra/core:mastraExecuteWithContext"
};

exports.mastraChannels = mastraChannels;
exports.mastraConfig = mastraConfig;
exports.mastraModuleNames = mastraModuleNames;
//# sourceMappingURL=mastra.js.map
