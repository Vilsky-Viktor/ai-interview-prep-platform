// Every supported language, in the order the backend lists them (prepza_common LANGUAGES).
export const LOCALES = [
  "en",
  "ru",
  "uk",
  "es",
  "pt",
  "de",
  "fr",
  "it",
  "pl",
  "nl",
  "tr",
  "ar",
  "he",
  "fa",
  "ja",
  "zh",
  "ko",
  "hi",
  "id",
  "th",
  "vi",
  "fil",
  "et",
] as const

// Written right to left: the whole page mirrors.
export const RTL_LOCALES: readonly Locale[] = ["ar", "he", "fa"]

export const DEFAULT_LOCALE = "en"

export const LOCALE_COOKIE = "prepza_locale"

export const LOCALE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

// Each language in its own words, as the settings page lists it.
export const LANGUAGE_NAMES: Record<Locale, string> = {
  en: "English",
  ru: "Русский",
  uk: "Українська",
  es: "Español",
  pt: "Português",
  de: "Deutsch",
  fr: "Français",
  it: "Italiano",
  pl: "Polski",
  nl: "Nederlands",
  tr: "Türkçe",
  ar: "العربية",
  he: "עברית",
  fa: "فارسی",
  ja: "日本語",
  zh: "中文（简体）",
  ko: "한국어",
  hi: "हिन्दी",
  id: "Bahasa Indonesia",
  th: "ไทย",
  vi: "Tiếng Việt",
  fil: "Filipino",
  et: "Eesti",
}

export type Locale = (typeof LOCALES)[number]
