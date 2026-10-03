Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const browser = require('@sentry/browser');
const core = require('@sentry/core');
const React = require('react');
const isSyntheticEvent = require('./isSyntheticEvent.js');

function init(options) {
  const opts = {
    ...options
  };
  core.applySdkMetadata(opts, "react");
  browser.setContext("react", { version: React.version });
  const client = browser.init(opts);
  core.setNormalizeStringifier(normalizeStringifyValue);
  return client;
}
function normalizeStringifyValue(value) {
  if (isSyntheticEvent.isSyntheticEvent(value)) {
    return "[SyntheticEvent]";
  }
  return browser.normalizeStringifyValue(value);
}

exports.init = init;
//# sourceMappingURL=sdk.js.map
