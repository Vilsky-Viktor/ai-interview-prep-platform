import type { KeyboardEvent } from "react"

/** ⌘/Ctrl + Enter sends every multi-line input; plain Enter adds a new line. */
export function isSubmitShortcut(event: KeyboardEvent) {
  return (
    event.key === "Enter" &&
    (event.metaKey || event.ctrlKey) &&
    !event.nativeEvent.isComposing
  )
}
