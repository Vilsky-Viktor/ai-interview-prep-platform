const dateFormat = new Intl.DateTimeFormat("en", { dateStyle: "medium" })

/** In the runtime's time zone, so the server and the browser can differ: lists rendered on both
put it in <time suppressHydrationWarning>, and the browser's local date wins. */
export function formatDate(iso: string) {
  return dateFormat.format(new Date(iso))
}

export function plural(count: number, word: string) {
  return `${count} ${word}${count === 1 ? "" : "s"}`
}
