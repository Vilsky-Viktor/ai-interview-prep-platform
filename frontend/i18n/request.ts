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

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  }
})
