function extractInfoFromServerReferenceId(id) {
  const infoByte = parseInt(id.slice(0, 2), 16);
  const typeBit = infoByte >> 7 & 1;
  const argMask = infoByte >> 1 & 63;
  const restArgs = infoByte & 1;
  const usedArgs = Array(6);
  for (let index = 0; index < 6; index++) {
    const bitPosition = 5 - index;
    const bit = argMask >> bitPosition & 1;
    usedArgs[index] = bit === 1;
  }
  return {
    type: typeBit === 1 ? "use-cache" : "server-action",
    usedArgs,
    hasRestArgs: restArgs === 1
  };
}
function isServerReference(value) {
  return value.$$typeof === /* @__PURE__ */ Symbol.for("react.server.reference");
}
function isUseCacheFunction(value) {
  if (!isServerReference(value)) {
    return false;
  }
  const { type } = extractInfoFromServerReferenceId(value.$$id);
  return type === "use-cache";
}

export { isUseCacheFunction };
//# sourceMappingURL=isUseCacheFunction.js.map
