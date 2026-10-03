Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const client = require('./client.js');
const breadcrumbs = require('./integrations/breadcrumbs.js');
const browserapierrors = require('./integrations/browserapierrors.js');
const browsersession = require('./integrations/browsersession.js');
const culturecontext = require('./integrations/culturecontext.js');
const globalhandlers = require('./integrations/globalhandlers.js');
const httpcontext = require('./integrations/httpcontext.js');
const linkederrors = require('./integrations/linkederrors.js');
const spotlight = require('./integrations/spotlight.js');
const stackParsers = require('./stack-parsers.js');
const fetch = require('./transports/fetch.js');
const normalizeStringifyValue = require('./normalizeStringifyValue.js');
const detectBrowserExtension = require('./utils/detectBrowserExtension.js');

function getDefaultIntegrations(_options) {
  return [
    core.eventFiltersIntegration(),
    core.functionToStringIntegration(),
    core.conversationIdIntegration(),
    browserapierrors.browserApiErrorsIntegration(),
    breadcrumbs.breadcrumbsIntegration(),
    core.consoleIntegration(),
    globalhandlers.globalHandlersIntegration(),
    linkederrors.linkedErrorsIntegration(),
    core.dedupeIntegration(),
    httpcontext.httpContextIntegration(),
    culturecontext.cultureContextIntegration(),
    browsersession.browserSessionIntegration()
  ];
}
function init(options = {}) {
  const shouldDisableBecauseIsBrowserExtenstion = !options.skipBrowserExtensionCheck && detectBrowserExtension.checkAndWarnIfIsEmbeddedBrowserExtension();
  let defaultIntegrations = options.defaultIntegrations == null ? getDefaultIntegrations() : options.defaultIntegrations;
  /*! rollup-include-development-only */
  if (options.spotlight) {
    if (!defaultIntegrations) {
      defaultIntegrations = [];
    }
    const args = typeof options.spotlight === "string" ? { sidecarUrl: options.spotlight } : void 0;
    defaultIntegrations.push(spotlight.spotlightBrowserIntegration(args));
  }
  /*! rollup-include-development-only-end */
  const integrations = core.getIntegrationsToSetup({
    integrations: options.integrations,
    defaultIntegrations
  });
  const clientOptions = {
    ...options,
    enabled: shouldDisableBecauseIsBrowserExtenstion ? false : options.enabled,
    stackParser: core.stackParserFromStackParserOptions(options.stackParser || stackParsers.defaultStackParser),
    integrations,
    transport: options.transport || fetch.makeFetchTransport
  };
  core.setNormalizeStringifier(normalizeStringifyValue.normalizeStringifyValue);
  return core.initAndBind(client.BrowserClient, clientOptions);
}
function forceLoad() {
}
function onLoad(callback) {
  callback();
}

exports.forceLoad = forceLoad;
exports.getDefaultIntegrations = getDefaultIntegrations;
exports.init = init;
exports.onLoad = onLoad;
//# sourceMappingURL=sdk.js.map
