import { describe, expect, it } from "vitest"

import {
  breadcrumbData,
  organizationData,
  softwareData,
} from "@/lib/structured-data"
import type { Catalog } from "@/types/billing"

const SITE = "https://prepza.example"

describe("softwareData", () => {
  it("offers the price per candidate from cheapest to dearest", () => {
    const catalog = {
      currency: "USD",
      candidate_prices: [
        { from_dollars: 0, cents: 300 },
        { from_dollars: 250, cents: 200 },
        { from_dollars: 1000, cents: 100 },
      ],
    } as Catalog

    expect(softwareData(SITE, "Tests.", catalog).offers).toEqual({
      "@type": "AggregateOffer",
      priceCurrency: "USD",
      lowPrice: 1,
      highPrice: 3,
      unitText: "candidate",
    })
  })
})

describe("breadcrumbData", () => {
  it("numbers each step from the home page with its full address", () => {
    const data = breadcrumbData(SITE, [
      { name: "prepza", path: "/" },
      { name: "Skills tests", path: "/tests" },
    ])

    expect(data.itemListElement).toEqual([
      { "@type": "ListItem", position: 1, name: "prepza", item: `${SITE}/` },
      {
        "@type": "ListItem",
        position: 2,
        name: "Skills tests",
        item: `${SITE}/tests`,
      },
    ])
  })
})

describe("organizationData", () => {
  it("names the brand without the logo's dot", () => {
    const [organization, website] = organizationData(SITE, "Tests.")

    expect(organization.name).toBe("prepza")
    expect(website.url).toBe(SITE)
  })
})
