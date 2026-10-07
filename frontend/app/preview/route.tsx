import { LOCALES, type Locale } from "@/constants/i18n"
import { PREVIEW_TITLE_MAX } from "@/constants/preview-image"
import { drawPreview } from "@/lib/preview-image"

/** A page's link preview picture: the logo over the page's title (lib/site.ts previewImage
 * names it for each page). A title's picture never changes, so it's cached for good. */
export async function GET(request: Request) {
  const query = new URL(request.url).searchParams
  const title = (query.get("title") ?? "").slice(0, PREVIEW_TITLE_MAX)
  const lang = query.get("lang") ?? ""
  const locale = LOCALES.includes(lang as Locale) ? (lang as Locale) : "en"
  const image = await drawPreview([title], locale)

  image.headers.set("Cache-Control", "public, max-age=31536000, immutable")

  return image
}
