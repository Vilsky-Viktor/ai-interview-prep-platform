Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const path = require('path');

const distDirRewriteFramesIntegration = core.defineIntegration(({ distDirName }) => {
  const distDirAbsPath = path.resolve(distDirName).replace(/(\/|\\)$/, "");
  const SOURCEMAP_FILENAME_REGEX = new RegExp(core.escapeStringForRegex(distDirAbsPath));
  const rewriteFramesInstance = core.rewriteFramesIntegration({
    iteratee: (frame) => {
      frame.filename = frame.filename?.replace(SOURCEMAP_FILENAME_REGEX, "app:///_next");
      return frame;
    }
  });
  return {
    ...rewriteFramesInstance,
    name: "DistDirRewriteFrames"
  };
});

exports.distDirRewriteFramesIntegration = distDirRewriteFramesIntegration;
//# sourceMappingURL=distDirRewriteFramesIntegration.js.map
