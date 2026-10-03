import { GLOBAL_OBJ } from '@sentry/core';

function getComponentName(elem, maxTraverseHeight = 5) {
  if (!GLOBAL_OBJ.HTMLElement) {
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

export { getComponentName };
//# sourceMappingURL=component-name.js.map
