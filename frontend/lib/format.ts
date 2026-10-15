/** A moment as a medium date in the language asked, in `timeZone` (the runtime's when none).
 * Pages show moments through useLocalTime or LocalDate, in the visitor's own time zone. */
export function formatDate(iso: string, locale: string, timeZone?: string) {
  return new Intl.DateTimeFormat(locale, {
    dateStyle: "medium",
    timeZone,
  }).format(new Date(iso))
}

/** A moment as a medium date and a short time in the language asked, in `timeZone` (the
 * runtime's when none), like formatDate. */
export function formatDateTime(iso: string, locale: string, timeZone?: string) {
  return new Intl.DateTimeFormat(locale, {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone,
  }).format(new Date(iso))
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

/** A count as the locale writes it short: 950, "1.5K", "250K", "1.2M". */
export function compactNumber(value: number, locale: string) {
  return new Intl.NumberFormat(locale, {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value)
}

/** Money short from $1,000 up ("$12.3K"); exact below it ("$66.60"). */
export function compactPrice(cents: number, currency: string, locale: string) {
  if (cents < 100_000) {
    return formatPrice(cents, currency, locale)
  }

  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(cents / 100)
}

/** A percentage (0 to 100) as the language writes it ("85 %" in French, "%85" in Turkish); "—"
 * for none (a grade not known yet). */
export function formatPercent(
  value: number | null | undefined,
  locale: string
) {
  return value == null
    ? "—"
    : new Intl.NumberFormat(locale, { style: "percent" }).format(value / 100)
}
