import * as fs from 'fs';
import * as path from 'path';

function hasOnlyAppRouterPages(projectDir) {
  const hasAppDir = ["app", path.join("src", "app")].some((dir) => isDirectory(path.join(projectDir, dir)));
  if (!hasAppDir) {
    return false;
  }
  return ["pages", path.join("src", "pages")].every((dir) => !containsNonApiPages(path.join(projectDir, dir)));
}
function containsNonApiPages(pagesDir) {
  if (!isDirectory(pagesDir)) {
    return false;
  }
  return fs.readdirSync(pagesDir).some((entry) => entry !== "api");
}
function isDirectory(dir) {
  try {
    return fs.statSync(dir).isDirectory();
  } catch {
    return false;
  }
}

export { hasOnlyAppRouterPages };
//# sourceMappingURL=pagesRouterDetection.js.map
