import type { MetadataRoute } from "next"

import { PRIVATE_PATHS } from "@/constants/seo"
import { siteUrl } from "@/lib/site"

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: PRIVATE_PATHS },
    sitemap: `${siteUrl()}/sitemap.xml`,
  }
}
