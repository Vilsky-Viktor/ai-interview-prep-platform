// `exact`: current only on that page itself; `wide`: hidden on phones, which have no room for
// it (the logo leads to the home page, and the footer has pricing).
export const NAV_LINKS = [
  { href: "/", label: "create", signedInOnly: false, exact: true, wide: true },
  {
    href: "/library",
    label: "explore",
    signedInOnly: false,
    exact: false,
    wide: false,
  },
  {
    href: "/preparations",
    label: "myKits",
    signedInOnly: true,
    exact: false,
    wide: false,
  },
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
