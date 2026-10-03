Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');

function getComponentName(elem, maxTraverseHeight = 5) {
  if (!core.GLOBAL_OBJ.HTMLElement) {
    return null;
  }
  let currentElem = elem;
  for (let i = 0; i < maxTraverseHeight; i++) {
    if (!currentElem) {
      return null;
    }
    if (currentElem instanceof HTMLElement) {
      if (currentElem.dataset["sentryComponent"]) {
        return currentElem.dataset["sentryComponent"];
      }
      if (currentElem.dataset["sentryElement"]) {
        return currentElem.dataset["sentryElement"];
      }
    }
    currentElem = currentElem.parentNode;
  }
  return null;
}

exports.getComponentName = getComponentName;
//# sourceMappingURL=component-name.js.map
