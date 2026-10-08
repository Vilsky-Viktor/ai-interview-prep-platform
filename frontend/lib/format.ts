/** In the runtime's time zone, so the server and the browser can differ: lists rendered on both
put it in <time suppressHydrationWarning>, and the browser's local date wins. */
export function formatDate(iso: string, locale: string) {
  return new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(
    new Date(iso)
  )
}

/** A calendar day ("2026-10-08") as a medium date in the language asked: the same day in every
 * time zone. */
export function formatDay(day: string, locale: string) {
  return new Intl.DateTimeFormat(locale, {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(day))
}

/** The browser's day today, as a date field takes it ("2026-10-08"). */
export function today(now = new Date()) {
  const month = String(now.getMonth() + 1).padStart(2, "0")
  const day = String(now.getDate()).padStart(2, "0")

  return `${now.getFullYear()}-${month}-${day}`
}

/** 2400 cents in USD: "$24". */
export function formatPrice(cents: number, currency: string, locale: string) {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    maximumFractionDigits: cents % 100 === 0 ? 0 : 2,
  }).format(cents / 100)
}

/** 100 to 300 cents in USD: "$1–$3", written as the locale writes a range. */
export function formatPriceRange(
  minCents: number,
  maxCents: number,
  currency: string,
  locale: string
) {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    maximumFractionDigits: minCents % 100 === 0 && maxCents % 100 === 0 ? 0 : 2,
  }).formatRange(minCents / 100, maxCents / 100)
}
