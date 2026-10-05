import { getRequestConfig } from "next-intl/server"
import { cookies, headers } from "next/headers"

import { DEFAULT_LOCALE, LOCALE_COOKIE } from "@/constants/i18n"
import { isLocale, preferredLocale } from "@/lib/locale"

// The interface language: the signed-in user's setting, which auth-provider.tsx keeps in a
// cookie. Without one (a first visit), the browser's preferred language if we support it.
export default getRequestConfig(async () => {
  const value = (await cookies()).get(LOCALE_COOKIE)?.value
  const locale =
    value && isLocale(value)
      ? value
      : (preferredLocale((await headers()).get("accept-language")) ??
        DEFAULT_LOCALE)

  const english = (await import("../messages/en.json")).default
  const messages =
    locale === DEFAULT_LOCALE
      ? english
      : withFallback(
          english,
          (await import(`../messages/${locale}.json`)).default
        )

  return { locale, messages }
})

type Messages = { [key: string]: string | string[] | Messages }

/** The translation, with English for any text it doesn't have yet: new text is written in English
 *  first and translated later (`pnpm check:messages` lists what's missing). */
function withFallback(english: Messages, translated: Messages): Messages {
  const merged: Messages = { ...english }

  for (const [key, value] of Object.entries(translated)) {
    const base = english[key]

    merged[key] =
      value &&
      typeof value === "object" &&
      !Array.isArray(value) &&
      base &&
      typeof base === "object" &&
      !Array.isArray(base)
        ? withFallback(base, value)
        : value
  }

  return merged
}
