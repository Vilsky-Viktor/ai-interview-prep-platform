Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const browserUtils = require('@sentry/browser-utils');
const core = require('@sentry/core');
const debugBuild = require('../debug-build.js');
const helpers = require('../helpers.js');

function checkAndWarnIfIsEmbeddedBrowserExtension() {
  if (_isEmbeddedBrowserExtension()) {
    if (debugBuild.DEBUG_BUILD) {
      core.consoleSandbox(() => {
        console.error(
          "[Sentry] You cannot use Sentry.init() in a browser extension, see: https://docs.sentry.io/platforms/javascript/best-practices/browser-extensions/"
        );
      });
    }
    return true;
  }
  return false;
}
function _isEmbeddedBrowserExtension() {
  if (typeof helpers.WINDOW.window === "undefined") {
    return false;
  }
  const _window = helpers.WINDOW;
  if (_window.nw) {
    return false;
  }
  const extensionObject = _window["chrome"] || _window["browser"];
  if (!extensionObject?.runtime?.id) {
    return false;
  }
  const href = browserUtils.getLocationHref();
  const isDedicatedExtensionPage = helpers.WINDOW === helpers.WINDOW.top && /^(?:chrome-extension|moz-extension|ms-browser-extension|safari-web-extension):\/\//.test(href);
  return !isDedicatedExtensionPage;
}

exports.checkAndWarnIfIsEmbeddedBrowserExtension = checkAndWarnIfIsEmbeddedBrowserExtension;
//# sourceMappingURL=detectBrowserExtension.js.map
