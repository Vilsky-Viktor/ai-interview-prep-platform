Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const react = require('@sentry/react');

const NEXTJS_INTERNAL_CHUNK_REGEX = /\/_next\/static\/chunks\/(main-|main-app-|polyfills-|webpack-|framework-|framework\.)[0-9a-f]+\.js(:\d+)*$/;
const nextjsClientStackFrameNormalizationIntegration = core.defineIntegration(
  ({
    assetPrefix,
    basePath,
    rewriteFramesAssetPrefixPath,
    experimentalThirdPartyOriginStackFrames
  }) => {
    const rewriteFramesInstance = react.rewriteFramesIntegration({
      // Turn `<origin>/<path>/_next/static/...` into `app:///_next/static/...`
      iteratee: (frame) => {
        if (experimentalThirdPartyOriginStackFrames) {
          const windowOrigin = typeof window !== "undefined" && window.location ? window.location.origin : "";
          if (frame.filename?.startsWith(windowOrigin) && !frame.filename.endsWith(".js")) {
            return frame;
          }
          if (assetPrefix) {
            if (frame.filename?.startsWith(assetPrefix)) {
              frame.filename = frame.filename.replace(assetPrefix, "app://");
            }
          } else if (basePath) {
            try {
              const { origin: frameOrigin } = new URL(frame.filename);
              if (frameOrigin === windowOrigin) {
                frame.filename = frame.filename?.replace(frameOrigin, "app://").replace(basePath, "");
              }
            } catch {
            }
          }
        } else {
          try {
            const { origin } = new URL(frame.filename);
            frame.filename = frame.filename?.replace(origin, "app://").replace(rewriteFramesAssetPrefixPath, "");
          } catch {
          }
        }
        if (experimentalThirdPartyOriginStackFrames) {
          if (frame.filename?.includes("/_next")) {
            frame.filename = decodeURI(frame.filename);
          }
        } else if (frame.filename?.startsWith("app:///_next")) {
          frame.filename = decodeURI(frame.filename);
        }
        if (frame.filename?.match(NEXTJS_INTERNAL_CHUNK_REGEX)) {
          frame.in_app = false;
        }
        return frame;
      }
    });
    return {
      ...rewriteFramesInstance,
      name: "NextjsClientStackFrameNormalization"
    };
  }
);

exports.nextjsClientStackFrameNormalizationIntegration = nextjsClientStackFrameNormalizationIntegration;
//# sourceMappingURL=clientNormalizationIntegration.js.map
