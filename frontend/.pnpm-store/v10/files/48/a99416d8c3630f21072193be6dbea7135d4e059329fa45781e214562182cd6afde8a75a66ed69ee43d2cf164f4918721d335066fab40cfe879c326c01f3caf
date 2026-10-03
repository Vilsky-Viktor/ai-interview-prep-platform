Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const debugBuild = require('../debug-build.js');
const isBuild = require('./isBuild.js');
const isUseCacheFunction = require('./isUseCacheFunction.js');

function shouldNoopSpan(callback) {
  const isBuildContext = isBuild.isBuild();
  const isUseCacheFunctionContext = callback ? isUseCacheFunction.isUseCacheFunction(callback) : false;
  if (isUseCacheFunctionContext) {
    debugBuild.DEBUG_BUILD && core.debug.log("Skipping span creation in Cache Components context");
  }
  return isBuildContext || isUseCacheFunctionContext;
}
function createNonRecordingSpan() {
  return new core.SentryNonRecordingSpan({
    traceId: "00000000000000000000000000000000",
    spanId: "0000000000000000"
  });
}
function startSpan(options, callback) {
  if (shouldNoopSpan(callback)) {
    return callback(createNonRecordingSpan());
  }
  return core.startSpan(options, callback);
}
function startSpanManual(options, callback) {
  if (shouldNoopSpan(callback)) {
    const nonRecordingSpan = createNonRecordingSpan();
    return callback(nonRecordingSpan, () => nonRecordingSpan.end());
  }
  return core.startSpanManual(options, callback);
}
function startInactiveSpan(options) {
  if (shouldNoopSpan()) {
    return createNonRecordingSpan();
  }
  return core.startInactiveSpan(options);
}

exports.startInactiveSpan = startInactiveSpan;
exports.startSpan = startSpan;
exports.startSpanManual = startSpanManual;
//# sourceMappingURL=nextSpan.js.map
