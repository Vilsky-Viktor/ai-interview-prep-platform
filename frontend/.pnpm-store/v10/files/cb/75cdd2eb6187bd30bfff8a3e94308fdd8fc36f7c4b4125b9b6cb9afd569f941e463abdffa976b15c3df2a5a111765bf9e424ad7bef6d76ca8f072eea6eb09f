Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const browser = require('@sentry/core/browser');
const types = require('../types.js');

function isMeasurementValue(value) {
  return typeof value === "number" && isFinite(value);
}
function startAndEndSpan(parentSpan, startTimeInSeconds, endTime, { ...ctx }) {
  const parentStartTime = core.spanToStaticSpanJSON(parentSpan).start_timestamp;
  if (parentStartTime && parentStartTime > startTimeInSeconds) {
    if (typeof parentSpan.updateStartTime === "function") {
      parentSpan.updateStartTime(startTimeInSeconds);
    }
  }
  return core.withActiveSpan(parentSpan, () => {
    const span = browser.startInactiveSpan({
      startTime: startTimeInSeconds,
      ...ctx
    });
    if (span) {
      span.end(endTime);
    }
    return span;
  });
}
function getBrowserPerformanceAPI() {
  return types.WINDOW.addEventListener && types.WINDOW.performance;
}
function msToSec(time) {
  return time / 1e3;
}
function extractNetworkProtocol(nextHopProtocol) {
  let name = "unknown";
  let version = "unknown";
  let _name = "";
  for (const char of nextHopProtocol) {
    if (char === "/") {
      [name, version] = nextHopProtocol.split("/");
      break;
    }
    if (!isNaN(Number(char))) {
      name = _name === "h" ? "http" : _name;
      version = nextHopProtocol.split(_name)[1];
      break;
    }
    _name += char;
  }
  if (_name === nextHopProtocol) {
    name = _name;
  }
  return { name, version };
}
function supportsWebVital(entryType) {
  try {
    return PerformanceObserver.supportedEntryTypes.includes(entryType);
  } catch {
    return false;
  }
}

exports.extractNetworkProtocol = extractNetworkProtocol;
exports.getBrowserPerformanceAPI = getBrowserPerformanceAPI;
exports.isMeasurementValue = isMeasurementValue;
exports.msToSec = msToSec;
exports.startAndEndSpan = startAndEndSpan;
exports.supportsWebVital = supportsWebVital;
//# sourceMappingURL=utils.js.map
