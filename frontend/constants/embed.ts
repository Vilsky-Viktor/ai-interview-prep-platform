// The interview a company's own site embeds in a frame (public/embed/v1.js makes the frame): its
// page, with the invite's token after it, in any language.
export const EMBED_PAGE = /^(?:\/[a-z]{2,3})?\/embedded\/([^/]+)$/

// Every message the frame sends the company's page says it's from prepza; the script listens for
// these kinds.
export const EMBED_SOURCE = "prepza"
export const EMBED_EVENTS = {
  ready: "ready",
  started: "started",
  finished: "finished",
  resize: "resize",
} as const

// How long the page waits for the company's domain before refusing to be framed.
export const EMBED_LOOKUP_TIMEOUT_MS = 3000
