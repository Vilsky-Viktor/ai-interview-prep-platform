const dateFormat = new Intl.DateTimeFormat("en", { dateStyle: "medium" })

/** In the runtime's time zone, so the server and the browser can differ: lists rendered on both
put it in <time suppressHydrationWarning>, and the browser's local date wins. */
export function formatDate(iso: string) {
  return dateFormat.format(new Date(iso))
}

export function plural(count: number, word: string) {
  return `${count} ${word}${count === 1 ? "" : "s"}`
}

/** "45 s", "2 min 5 s". */
export function formatSeconds(seconds: number) {
  const minutes = Math.floor(seconds / 60)
  const rest = seconds % 60

  if (minutes === 0) {
    return `${rest} s`
  }

  return rest === 0 ? `${minutes} min` : `${minutes} min ${rest} s`
}

/** 2400 cents in USD: "$24". */
export function formatPrice(cents: number, currency: string) {
  return new Intl.NumberFormat("en", {
    style: "currency",
    currency,
    maximumFractionDigits: cents % 100 === 0 ? 0 : 2,
  }).format(cents / 100)
}
