import { DEFAULT_LOCALE, LOCALES } from "@/constants/i18n"
import {
  LOCALIZED_ARTICLE,
  LOCALIZED_PATHS,
  PRIVATE_PATHS,
} from "@/constants/seo"
import { isLocale } from "@/lib/locale"

/** Whether a page has an address in every language: the listed pages and the articles. */
export function isLocalizedPath(path: string) {
  return LOCALIZED_PATHS.includes(path) || LOCALIZED_ARTICLE.test(path)
}

/** A localized page's address in `locale`: English without a prefix ("/pricing"), the others
 * under theirs ("/de/pricing", "/de" for the home page). */
export function localizedPath(locale: string, path: string) {
  if (locale === DEFAULT_LOCALE) {
    return path
  }

  return path === "/" ? `/${locale}` : `/${locale}${path}`
}

/** A link from a page served under `locale`'s address (null: the plain one) to `href`: to that
 * language's version when the target has one ("/faq" from /de/pricing is "/de/faq"). */
export function localizeHref(locale: string | null, href: string) {
  const cut = href.search(/[?#]/)
  const [path, rest] =
    cut < 0 ? [href, ""] : [href.slice(0, cut), href.slice(cut)]

  return locale && isLocalizedPath(path)
    ? `${localizedPath(locale, path)}${rest}`
    : href
}

/** A localized page's address in every language (or in `locales`, the ones it's written in),
 * and English as the default, for hreflang. */
export function languageAlternates(
  path: string,
  locales: readonly string[] = LOCALES
): Record<string, string> {
  return {
    ...Object.fromEntries(
      locales.map((locale) => [locale, localizedPath(locale, path)])
    ),
    "x-default": path,
  }
}

/** The language and page of an address under a language prefix ("/de/pricing" gives de and
 * /pricing); none for other addresses, English's prefix included, or a page that has no
 * language versions. */
export function splitLocale(pathname: string) {
  const [, first, ...rest] = pathname.split("/")
  const path = `/${rest.join("/")}`.replace(/\/$/, "") || "/"

  if (!first || !isLocale(first) || first === DEFAULT_LOCALE) {
    return null
  }

  return isLocalizedPath(path) ? { locale: first, path } : null
}

/** Whether an address is a private page: signed-in areas and personal links, kept out of search
 * results. "/practice/*\/start" stands for any one segment. */
export function isPrivatePath(pathname: string) {
  return PRIVATE_PATHS.some((prefix) => {
    const pattern = prefix.replace(/\*/g, "[^/]+").replace(/\/$/, "")

    return new RegExp(`^${pattern}(/|$)`).test(pathname)
  })
}
