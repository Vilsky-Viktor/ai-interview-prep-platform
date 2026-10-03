import { defineIntegration, escapeStringForRegex, rewriteFramesIntegration } from '@sentry/core';

const distDirRewriteFramesIntegration = defineIntegration(({ distDirName }) => {
  const distDirAbsPath = distDirName.replace(/(\/|\\)$/, "");
  const SOURCEMAP_FILENAME_REGEX = new RegExp(`.*${escapeStringForRegex(distDirAbsPath)}`);
  const rewriteFramesIntegrationInstance = rewriteFramesIntegration({
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

export { distDirRewriteFramesIntegration };
//# sourceMappingURL=distDirRewriteFramesIntegration.js.map
