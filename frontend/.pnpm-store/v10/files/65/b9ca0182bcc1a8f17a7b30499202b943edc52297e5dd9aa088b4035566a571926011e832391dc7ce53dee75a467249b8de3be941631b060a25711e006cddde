Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');

const distDirRewriteFramesIntegration = core.defineIntegration(({ distDirName }) => {
  const distDirAbsPath = distDirName.replace(/(\/|\\)$/, "");
  const SOURCEMAP_FILENAME_REGEX = new RegExp(`.*${core.escapeStringForRegex(distDirAbsPath)}`);
  const rewriteFramesIntegrationInstance = core.rewriteFramesIntegration({
    iteratee: (frame) => {
      frame.filename = frame.filename?.replace(SOURCEMAP_FILENAME_REGEX, "app:///_next");
      return frame;
    }
  });
  return {
    ...rewriteFramesIntegrationInstance,
    name: "DistDirRewriteFrames"
  };
});

exports.distDirRewriteFramesIntegration = distDirRewriteFramesIntegration;
//# sourceMappingURL=distDirRewriteFramesIntegration.js.map
