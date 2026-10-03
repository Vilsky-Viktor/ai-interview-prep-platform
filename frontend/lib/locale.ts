import {
  LOCALE_COOKIE,
  LOCALE_COOKIE_MAX_AGE,
  LOCALES,
  type Locale,
} from "@/constants/i18n"

export function isLocale(value: string): value is Locale {
  return (LOCALES as readonly string[]).includes(value)
}

export function readLocaleCookie() {
  return document.cookie
    .split("; ")
    .find((item) => item.startsWith(`${LOCALE_COOKIE}=`))
    ?.split("=")[1]
}

export function writeLocaleCookie(locale: Locale) {
  const secure = location.protocol === "https:" ? "; secure" : ""
  document.cookie = `${LOCALE_COOKIE}=${locale}; path=/; max-age=${LOCALE_COOKIE_MAX_AGE}; samesite=lax${secure}`
}

/** The first supported language in an Accept-Language header, by preference ("uk-UA,
 * ru;q=0.8" gives uk), or none. */
export function preferredLocale(header: string | null) {
  const tags = (header ?? "").split(",").map((part) => {
    const [tag, ...params] = part.trim().split(";")
    const quality = params.find((param) => param.trim().startsWith("q="))

    return {
      code: tag.split("-")[0].toLowerCase(),
      quality: quality ? Number(quality.trim().slice(2)) : 1,
    }
  })

  return tags
    .filter((item) => item.quality > 0)
    .sort((a, b) => b.quality - a.quality)
    .map((item) => item.code)
    .find(isLocale)
}
