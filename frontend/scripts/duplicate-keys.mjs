// Keys written twice in one object: JSON.parse keeps the last silently, so a new message can
// replace an old one with the same name. Read from the raw text, each object's keys apart.
export const duplicateKeys = (text) => {
  const found = []
  // The open objects (a set of their keys) and lists (null), innermost last.
  const open = []
  let expectKey = false
  for (let index = 0; index < text.length; index++) {
    const char = text[index]
    if (char === '"') {
      let end = index + 1
      while (text[end] !== '"') end += text[end] === "\\" ? 2 : 1
      if (expectKey) {
        const key = JSON.parse(text.slice(index, end + 1))
        if (open.at(-1).has(key)) found.push(key)
        open.at(-1).add(key)
        expectKey = false
      }
      index = end
    } else if (char === "{") {
      open.push(new Set())
      expectKey = true
    } else if (char === "[") open.push(null)
    else if (char === "}" || char === "]") open.pop()
    else if (char === ",") expectKey = open.at(-1) instanceof Set
  }
  return found
}
