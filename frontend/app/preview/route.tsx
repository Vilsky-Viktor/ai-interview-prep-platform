import { LOCALES, type Locale } from "@/constants/i18n"
import { PREVIEW_TITLE_MAX } from "@/constants/preview-image"
import { drawPreview } from "@/lib/preview-image"

/** A page's link preview picture: the logo over the page's title (lib/site.ts previewImage
 * names it for each page). A title's picture never changes, so it's cached for good. It's kept
 * out of image search by its header, not robots.txt: link preview bots such as X's and
 * LinkedIn's follow robots.txt and would show no picture. */
export async function GET(request: Request) {
  const query = new URL(request.url).searchParams
  const title = (query.get("title") ?? "").slice(0, PREVIEW_TITLE_MAX)
  const lang = query.get("lang") ?? ""
  const locale = LOCALES.includes(lang as Locale) ? (lang as Locale) : "en"
  const image = await drawPreview([title], locale)

  image.headers.set("Cache-Control", "public, max-age=31536000, immutable")
  image.headers.set("X-Robots-Tag", "noindex")

  return image
}
