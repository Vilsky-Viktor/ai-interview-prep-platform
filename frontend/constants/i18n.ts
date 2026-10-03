export const LOCALES = ["en", "ru"] as const

export const DEFAULT_LOCALE = "en"

export const LOCALE_COOKIE = "prepza_locale"

export const LOCALE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

// Each language in its own words, as the settings page lists it.
export const LANGUAGE_NAMES: Record<Locale, string> = {
  en: "English",
  ru: "Русский",
}

export type Locale = (typeof LOCALES)[number]
