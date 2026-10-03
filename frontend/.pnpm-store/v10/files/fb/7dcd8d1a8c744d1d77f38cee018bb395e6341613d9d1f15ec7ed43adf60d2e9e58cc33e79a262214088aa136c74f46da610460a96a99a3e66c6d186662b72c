import { startInactiveSpan as startInactiveSpan$1, startSpan as startSpan$1, startSpanManual as startSpanManual$1, debug, SentryNonRecordingSpan } from '@sentry/core';
import { DEBUG_BUILD } from '../debug-build.js';
import { isBuild } from './isBuild.js';
import { isUseCacheFunction } from './isUseCacheFunction.js';

function shouldNoopSpan(callback) {
  const isBuildContext = isBuild();
  const isUseCacheFunctionContext = callback ? isUseCacheFunction(callback) : false;
  if (isUseCacheFunctionContext) {
    DEBUG_BUILD && debug.log("Skipping span creation in Cache Components context");
  }
  return isBuildContext || isUseCacheFunctionContext;
}
function createNonRecordingSpan() {
  return new SentryNonRecordingSpan({
    traceId: "00000000000000000000000000000000",
    spanId: "0000000000000000"
  });
}
function startSpan(options, callback) {
  if (shouldNoopSpan(callback)) {
    return callback(createNonRecordingSpan());
  }
  return startSpan$1(options, callback);
}
function startSpanManual(options, callback) {
  if (shouldNoopSpan(callback)) {
    const nonRecordingSpan = createNonRecordingSpan();
    return callback(nonRecordingSpan, () => nonRecordingSpan.end());
  }
  return startSpanManual$1(options, callback);
}
function startInactiveSpan(options) {
  if (shouldNoopSpan()) {
    return createNonRecordingSpan();
  }
  return startInactiveSpan$1(options);
}

export { startInactiveSpan, startSpan, startSpanManual };
//# sourceMappingURL=nextSpan.js.map
