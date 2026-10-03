Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');

const WINDOW = core.GLOBAL_OBJ;
const DEFAULT_LINES_OF_CONTEXT = 5;
const INTEGRATION_NAME = "ContextLines";
const _contextLinesIntegration = ((options = {}) => {
  return {
    name: INTEGRATION_NAME,
    processEvent(event, _hint, client) {
      const contextLines = options.frameContextLines ?? client?.getDataCollectionOptions().frameContextLines ?? DEFAULT_LINES_OF_CONTEXT;
      return addSourceContext(event, contextLines);
    }
  };
});
const contextLinesIntegration = core.defineIntegration(_contextLinesIntegration);
function addSourceContext(event, contextLines) {
  const doc = WINDOW.document;
  const htmlFilename = WINDOW.location && core.stripUrlQueryAndFragment(WINDOW.location.href);
  if (!doc || !htmlFilename) {
    return event;
  }
  const exceptions = event.exception?.values;
  if (!exceptions?.length) {
    return event;
  }
  const html = doc.documentElement.innerHTML;
  if (!html) {
    return event;
  }
  const htmlLines = ["<!DOCTYPE html>", "<html>", ...html.split("\n"), "</html>"];
  exceptions.forEach((exception) => {
    const stacktrace = exception.stacktrace;
    if (stacktrace?.frames) {
      stacktrace.frames = stacktrace.frames.map(
        (frame) => applySourceContextToFrame(frame, htmlLines, htmlFilename, contextLines)
      );
    }
  });
  return event;
}
function applySourceContextToFrame(frame, htmlLines, htmlFilename, linesOfContext) {
  if (frame.filename !== htmlFilename || !frame.lineno || !htmlLines.length) {
    return frame;
  }
  core.addContextToFrame(htmlLines, frame, linesOfContext);
  return frame;
}

exports.applySourceContextToFrame = applySourceContextToFrame;
exports.contextLinesIntegration = contextLinesIntegration;
//# sourceMappingURL=contextlines.js.map
