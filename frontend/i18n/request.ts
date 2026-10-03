import { getRequestConfig } from "next-intl/server"
import { cookies } from "next/headers"

import { DEFAULT_LOCALE, LOCALE_COOKIE } from "@/constants/i18n"
import { isLocale } from "@/lib/locale"

// The interface language: the signed-in user's setting, which auth-provider.tsx keeps in a cookie.
export default getRequestConfig(async () => {
  const value = (await cookies()).get(LOCALE_COOKIE)?.value
  const locale = value && isLocale(value) ? value : DEFAULT_LOCALE

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  }
})
