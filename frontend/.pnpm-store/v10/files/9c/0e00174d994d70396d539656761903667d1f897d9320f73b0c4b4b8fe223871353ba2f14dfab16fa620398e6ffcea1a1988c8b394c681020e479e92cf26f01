Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const browserUtils = require('@sentry/browser-utils');
const attributes = require('@sentry/conventions/attributes');
const op = require('@sentry/conventions/op');
const debugBuild = require('../debug-build.js');

const INTEGRATION_NAME = "SpotlightBrowser";
const SPOTLIGHT_IGNORE_SPANS = [
  { op: op.UI_INTERACTION_CLICK, name: "#sentry-spotlight" },
  { op: op.UI_INTERACTION_CLICK, attributes: { [attributes.BROWSER_WEB_VITAL_INP_TARGET]: "#sentry-spotlight" } }
];
const _spotlightIntegration = ((options = {}) => {
  const sidecarUrl = options.sidecarUrl || "http://localhost:8969/stream";
  return {
    name: INTEGRATION_NAME,
    setup: () => {
      debugBuild.DEBUG_BUILD && core.debug.log("Using Sidecar URL", sidecarUrl);
    },
    beforeSetup(client) {
      const opts = client.getOptions();
      opts.ignoreSpans = [...opts.ignoreSpans || [], ...SPOTLIGHT_IGNORE_SPANS];
    },
    afterAllSetup: (client) => {
      setupSidecarForwarding(client, sidecarUrl);
    }
  };
});
function setupSidecarForwarding(client, sidecarUrl) {
  const makeFetch = browserUtils.getNativeImplementation("fetch");
  let failCount = 0;
  client.on("beforeEnvelope", (envelope) => {
    if (failCount > 3) {
      core.debug.warn("[Spotlight] Disabled Sentry -> Spotlight integration due to too many failed requests:", failCount);
      return;
    }
    makeFetch(sidecarUrl, {
      method: "POST",
      body: core.serializeEnvelope(envelope),
      headers: {
        "Content-Type": "application/x-sentry-envelope"
      },
      mode: "cors"
    }).then(
      (res) => {
        if (res.status >= 200 && res.status < 400) {
          failCount = 0;
        }
      },
      (err) => {
        failCount++;
        core.debug.error(
          "Sentry SDK can't connect to Sidecar is it running? See: https://spotlightjs.com/sidecar/npx/",
          err
        );
      }
    );
  });
}
const spotlightBrowserIntegration = core.defineIntegration(_spotlightIntegration);

exports.INTEGRATION_NAME = INTEGRATION_NAME;
exports.SPOTLIGHT_IGNORE_SPANS = SPOTLIGHT_IGNORE_SPANS;
exports.spotlightBrowserIntegration = spotlightBrowserIntegration;
//# sourceMappingURL=spotlight.js.map
