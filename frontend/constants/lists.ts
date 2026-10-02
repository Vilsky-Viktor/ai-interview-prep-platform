// Items a list asks the API for at a time; the next page loads as the user nears the end.
export const PAGE_SIZE = 20

// Start loading the next page when this many items are left below the viewport.
export const LOAD_AHEAD = 5

// Rows rendered beyond the viewport, so fast scrolling doesn't show blanks.
export const OVERSCAN = 6

// The viewport assumed before the browser can measure (server rendering), so the first rows
// render on the server instead of appearing only once the page's JavaScript runs.
export const INITIAL_VIEWPORT = { width: 1024, height: 1000 }
