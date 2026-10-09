// How far a page is scrolled (px) before the "back to top" button shows: about a screen.
export const SCROLL_TOP_AFTER_PX = 800

// The pages where questions run against the clock (an interview, a practice round, a company's
// preview), in any language: no header or footer there, only the questions.
export const TIMED_PAGE = /^(\/[a-z]{2,3})?\/sessions\//
