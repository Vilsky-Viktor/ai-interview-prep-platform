import { FOUNDER } from "@/constants/about"
import { SITE_NAME } from "@/constants/seo"
import type { Catalog } from "@/types/billing"

// schema.org structured data for search engines and AI answers: who makes prepza, what it is and
// costs, and where a page sits. `site` is the site's address (lib/site.ts siteUrl).

const CONTEXT = "https://schema.org"
const BRAND = SITE_NAME.replace(/\.$/, "")

/** The company and the site, for the home page. */
export function organizationData(site: string, description: string) {
  return [
    {
      "@context": CONTEXT,
      "@type": "Organization",
      name: BRAND,
      url: site,
      logo: `${site}/icon.svg`,
      founder: { "@type": "Person", name: FOUNDER.name },
      sameAs: [FOUNDER.linkedin],
    },
    {
      "@context": CONTEXT,
      "@type": "WebSite",
      name: BRAND,
      url: site,
      description,
    },
  ]
}

/** prepza as a product with its price per candidate, cheapest to dearest, for the pricing
 * page. */
export function softwareData(
  site: string,
  description: string,
  catalog: Catalog
) {
  const cents = catalog.candidate_prices.map((price) => price.cents)

  return {
    "@context": CONTEXT,
    "@type": "SoftwareApplication",
    name: BRAND,
    url: site,
    description,
    applicationCategory: "BusinessApplication",
    operatingSystem: "Web",
    offers: {
      "@type": "AggregateOffer",
      priceCurrency: catalog.currency,
      lowPrice: Math.min(...cents) / 100,
      highPrice: Math.max(...cents) / 100,
      unitText: "candidate",
    },
  }
}

/** The founder, for the about page. */
export function personData(site: string) {
  return {
    "@context": CONTEXT,
    "@type": "Person",
    name: FOUNDER.name,
    image: `${site}${FOUNDER.photo}`,
    sameAs: [FOUNDER.linkedin],
    worksFor: { "@type": "Organization", name: BRAND, url: site },
  }
}

/** Where a page sits under the home page: each step's name and path, the page itself last. */
export function breadcrumbData(
  site: string,
  steps: { name: string; path: string }[]
) {
  return {
    "@context": CONTEXT,
    "@type": "BreadcrumbList",
    itemListElement: steps.map((step, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: step.name,
      item: `${site}${step.path}`,
    })),
  }
}

/** An article (a guide, a comparison or a pillar page) with its dates. */
export function articleData(
  site: string,
  page: { title: string; description: string; path: string; updated: string }
) {
  return {
    "@context": CONTEXT,
    "@type": "Article",
    headline: page.title,
    description: page.description,
    url: `${site}${page.path}`,
    dateModified: page.updated,
    author: { "@type": "Person", name: FOUNDER.name, url: `${site}/about` },
    publisher: { "@type": "Organization", name: BRAND, url: site },
  }
}
