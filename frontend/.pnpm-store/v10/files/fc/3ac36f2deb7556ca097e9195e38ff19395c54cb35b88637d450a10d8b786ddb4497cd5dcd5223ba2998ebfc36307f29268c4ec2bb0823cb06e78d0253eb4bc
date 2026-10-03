import { defineIntegration, escapeStringForRegex, rewriteFramesIntegration } from '@sentry/core';
import * as path from 'path';

const distDirRewriteFramesIntegration = defineIntegration(({ distDirName }) => {
  const distDirAbsPath = path.resolve(distDirName).replace(/(\/|\\)$/, "");
  const SOURCEMAP_FILENAME_REGEX = new RegExp(escapeStringForRegex(distDirAbsPath));
  const rewriteFramesInstance = rewriteFramesIntegration({
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

export { distDirRewriteFramesIntegration };
//# sourceMappingURL=distDirRewriteFramesIntegration.js.map
