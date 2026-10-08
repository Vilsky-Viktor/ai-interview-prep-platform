// `exact`: current only on that page itself; `wide`: hidden on phones, which have no room for
// it (the logo leads to the home page, and the footer has pricing).
export const NAV_LINKS = [
  {
    href: "/companies",
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

// The footer's links in three columns: for companies, legal, and help; `label` is the nav
// message.
export const FOOTER_COLUMNS = [
  [
    { href: "/tests", label: "tests" },
    { href: "/pre-employment-testing", label: "preEmploymentTesting" },
    { href: "/ai-interviews", label: "aiInterviews" },
    { href: "/compare", label: "compare" },
    { href: "/guides", label: "guides" },
  ],
  [
    { href: "/privacy", label: "privacy" },
    { href: "/terms", label: "terms" },
    { href: "/documents", label: "docs" },
    { href: "/api-docs", label: "apiDocs" },
  ],
  [
    { href: "/practice", label: "practice" },
    { href: "/faq", label: "faq" },
    { href: "/about", label: "about" },
    { href: "/contact", label: "contact" },
  ],
] as const
