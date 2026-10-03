/** In the runtime's time zone, so the server and the browser can differ: lists rendered on both
put it in <time suppressHydrationWarning>, and the browser's local date wins. */
export function formatDate(iso: string, locale: string) {
  return new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(
    new Date(iso)
  )
}

/** 2400 cents in USD: "$24". */
export function formatPrice(cents: number, currency: string, locale: string) {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    maximumFractionDigits: cents % 100 === 0 ? 0 : 2,
  }).format(cents / 100)
}
