// `exact`: current only on that page itself; `wide`: hidden on phones, which have no room for
// it (the logo leads to the home page, and the footer has pricing).
export const NAV_LINKS = [
  {
    href: "/company",
    label: "hiring",
    signedInOnly: false,
    exact: false,
    wide: false,
  },
  {
    href: "/pricing",
    label: "pricingLink",
    signedInOnly: false,
    exact: false,
    wide: true,
  },
] as const
