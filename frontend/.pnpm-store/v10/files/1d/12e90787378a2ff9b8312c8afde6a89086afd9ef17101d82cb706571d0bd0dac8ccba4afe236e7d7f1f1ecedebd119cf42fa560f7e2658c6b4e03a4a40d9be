Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');

function reportPageLoaded(client = core.getClient()) {
  client?.emit("endPageloadSpan");
}

exports.reportPageLoaded = reportPageLoaded;
//# sourceMappingURL=reportPageLoaded.js.map
